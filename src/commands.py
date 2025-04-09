from telegram import Update
from telegram.ext import ContextTypes
from widget.carousel import CarouselWidget
from database.database_postgreSQL_pgrouting_sample import DatabasePostgreSQLPgRoutingSample
from database.database_postgreSQL_polito_paths import DatabasePostgreSQLPolitoPaths
from utils.log import Log
from enum import Enum


class SampleQuestionsStepState(Enum):
    STEP1 = "start"
    STEP2 = "destination"
    STEP3 = "shortest_path"
    
class SampleRoom(Enum):
    EMERGENCY = 1
    CARDIOLOGY = 2
    PEDIATRICS = 3
    ONCOLOGY = 4
    RADIOLOGY = 5
    SURGERY = 6
    PHARMACY = 7


class Commands:
    def __init__(self, db_pg_routing_sample: DatabasePostgreSQLPgRoutingSample, db_polito_paths: DatabasePostgreSQLPolitoPaths):
        self.log = Log("Commands")
        self.db_pg_routing_sample = db_pg_routing_sample
        self.db_polito_paths = db_polito_paths
        self.active_carousels = {}  # Stores user-specific carousel and state

    async def sample(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            query = "SELECT name FROM departments"
            with self.db_pg_routing_sample as db:
                results = db.execute_query(query)

            # Process results to ensure they are a list of strings
            if isinstance(results, list):
                processed_results = [row[0] if isinstance(row, (list, tuple)) else row for row in results]
                if not all(isinstance(item, str) for item in processed_results):
                    raise ValueError("Query results must be a list of strings.")
            else:
                raise ValueError("Query results must be a list.")

            user_id = update.effective_user.id
            carousel = CarouselWidget("Select the starting point", processed_results)
            self.active_carousels[user_id] = {"carousel": carousel, "state": SampleQuestionsStepState.STEP1}

            await update.message.reply_text(carousel.message, reply_markup=carousel.get_keyboard())
        except ValueError as ve:
            self.log.error(f"Invalid query results: {ve}")
            await update.message.reply_text("An error occurred: Query results are not valid.")
        except Exception as e:
            self.log.error(f"Error executing 'sample' command: {e}")
            await update.message.reply_text("An error occurred while executing the command.")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        clb_query = update.callback_query
        await clb_query.answer()

        user_id = clb_query.from_user.id
        if user_id not in self.active_carousels:
            await clb_query.edit_message_text("No active carousel found.")
            return

        user_data = self.active_carousels[user_id]
        carousel = user_data["carousel"]
        state = user_data["state"]
        data = clb_query.data

        if data.startswith("select:"):
            selected_value = data.split(":", 1)[1]

            if state == SampleQuestionsStepState.STEP1:
                # Step 3: Output a message with the selected starting point
                user_data["start_point"] = selected_value
                await clb_query.edit_message_text(f"You start from {selected_value}")

                # Step 4: Show another carousel for selecting the destination point
                new_carousel = CarouselWidget("Select the destination point", carousel.items)
                self.active_carousels[user_id] = {"carousel": new_carousel, "state": SampleQuestionsStepState.STEP2, "start_point": selected_value}
                await clb_query.message.reply_text(new_carousel.message, reply_markup=new_carousel.get_keyboard())

            elif state == SampleQuestionsStepState.STEP2:
                # Step 6: Output a message with the selected destination point
                user_data["destination_point"] = selected_value
                await clb_query.edit_message_text(f"You want to arrive to {selected_value}")

                # Move to STEP3 and execute the shortest path calculation
                self.active_carousels[user_id].update({"state": SampleQuestionsStepState.STEP3, "destination_point": selected_value})


                # Step 7: Compute the shortest path
                try:
                    self.log.info(f"Calculating shortest path from {self.active_carousels[user_id]['start_point'].upper()} to {self.active_carousels[user_id]['destination_point'].upper()}")
                    start_point = SampleRoom[ self.active_carousels[user_id]['start_point'].upper()].value
                    destination_point = SampleRoom[self.active_carousels[user_id]['destination_point'].upper()].value
                    
                    # Query the database for the shortest path
                    query = f"SELECT * FROM get_navigation_instructions({start_point}, {destination_point});"
                    with self.db_pg_routing_sample as db:
                        results = db.execute_query(query)
                        
                    # Convert the results into a map structure
                    map_structure = [
                        {
                            "step": row[0],
                            "instruction": row[1],
                            "cost": row[2],
                            "geometry": row[3]
                        }
                        for row in results
                    ]

                    # Log the map structure for debugging purposes
                    self.log.info(f"Map structure: {map_structure}")

                    # Format the results for the user
                    if map_structure:
                        for step in map_structure:
                            await context.bot.send_message(
                                chat_id=clb_query.from_user.id,
                                text=f"Step {step['step']}: {step['instruction']} for {round(step['cost'], 1)}m"
                            )
                    else:
                        await context.bot.send_message(
                            chat_id=clb_query.from_user.id,
                            text="No path found between the selected points."
                        )

                except Exception as e:
                    self.log.error(f"Error querying shortest path: {e}")
                    await context.bot.send_message(
                        chat_id=clb_query.from_user.id,
                        text="An error occurred while calculating the shortest path."
                    )


                # Optionally, clean up the user's carousel data
                del self.active_carousels[user_id]

        elif data.startswith("navigate:"):
            # Handle navigation
            direction = data.split(":", 1)[1]
            if direction == "prev" and carousel.current_page > 0:
                carousel.current_page -= 1
            elif direction == "next" and (carousel.current_page + 1) * carousel.items_per_page < len(carousel.items):
                carousel.current_page += 1
            # Update the message with the new page
            await clb_query.edit_message_text(carousel.message, reply_markup=carousel.get_keyboard())

    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await update.message.reply_text("This command does not exist!")
        except Exception as e:
            raise



