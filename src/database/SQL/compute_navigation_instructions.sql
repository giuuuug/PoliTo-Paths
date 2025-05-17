CREATE OR REPLACE FUNCTION compute_navigation_instructions(source_id integer, target_id integer)
RETURNS TABLE(
    step_number integer,
    direction text,
    distance_meters numeric,
    next_turn text,
    landmark_name varchar,
    path_geometry geometry
) AS
$$
BEGIN
    RETURN QUERY
    WITH route AS (
        SELECT 
            r.seq,
            r.node,
            p.wkb_geometry AS point_geom,
            path.wkb_geometry AS path_geom,
            -- Trova i punti di riferimento vicini
            CAST((
                SELECT string_agg(DISTINCT nearby.room_names, ', ')
                FROM xs01_p nearby
                WHERE nearby.room_names IS NOT NULL 
                AND ST_DWithin(p.wkb_geometry, nearby.wkb_geometry, 10)  -- Cerca punti entro 10 metri
                AND nearby.id_0 != r.node  -- Esclude il punto corrente
            ) AS varchar) AS nearby_landmarks,
            -- Calcola la direzione usando l'angolo tra segmenti
            CASE
                WHEN ST_Azimuth(
                    LAG(p.wkb_geometry) OVER (ORDER BY r.seq),
                    p.wkb_geometry
                ) IS NOT NULL AND
                     ST_Azimuth(
                    p.wkb_geometry,
                    LEAD(p.wkb_geometry) OVER (ORDER BY r.seq)
                ) IS NOT NULL 
                THEN
                    CASE
                        WHEN degrees(
                            ST_Azimuth(
                                LAG(p.wkb_geometry) OVER (ORDER BY r.seq),
                                p.wkb_geometry
                            ) -
                            ST_Azimuth(
                                p.wkb_geometry,
                                LEAD(p.wkb_geometry) OVER (ORDER BY r.seq)
                            )
                        ) BETWEEN 30 AND 180 THEN 'Turn right'
                        WHEN degrees(
                            ST_Azimuth(
                                LAG(p.wkb_geometry) OVER (ORDER BY r.seq),
                                p.wkb_geometry
                            ) -
                            ST_Azimuth(
                                p.wkb_geometry,
                                LEAD(p.wkb_geometry) OVER (ORDER BY r.seq)
                            )
                        ) BETWEEN -180 AND -30 THEN 'Turn left'
                        ELSE 'Continue straight'
                    END
                ELSE NULL
            END as turn_direction,
            -- Calcola la distanza fino al prossimo punto
            ST_Distance(
                p.wkb_geometry,
                LEAD(p.wkb_geometry) OVER (ORDER BY r.seq)
            ) as segment_distance
        FROM pgr_dijkstra(
            'SELECT ogc_fid AS id, source, target, cost FROM xs01_path',
            source_id,
            target_id,
            directed := false
        ) r
        LEFT JOIN xs01_p p ON r.node = p.id_0
        LEFT JOIN xs01_path path ON r.edge = path.ogc_fid
    )
    SELECT
        r.seq as step_number,
        r.turn_direction as direction,
        ROUND(r.segment_distance::numeric * 100) / 100 as distance_meters,
        LEAD(r.turn_direction) OVER (ORDER BY r.seq) as next_turn,
        r.nearby_landmarks as landmark_name,
        r.path_geom as path_geometry
    FROM route r
    WHERE r.turn_direction IS NOT NULL
    ORDER BY r.seq;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION compute_navigation_instructions IS 'Calcola le istruzioni di navigazione con direzioni, distanze e punti di riferimento';

