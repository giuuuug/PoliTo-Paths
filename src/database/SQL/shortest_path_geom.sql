CREATE OR REPLACE FUNCTION shortest_path_geom(source_id integer, target_id integer)
RETURNS TABLE(
    seq integer,
    node integer,
    node_geom geometry(Point, 4326),
    edge integer,
    edge_geom geometry(LineString, 4326),
    cost double precision
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.seq::integer,
        d.node::integer,
        n.wkb_geometry AS node_geom,
        d.edge::integer,
        e.wkb_geometry AS edge_geom,
        d.cost
    FROM pgr_dijkstra(
        'SELECT ogc_fid AS id, source, target, cost FROM xs01_path',
        source_id,
        target_id,
        directed := false
    ) d
    LEFT JOIN xs01_p n ON d.node = n.id_0
    LEFT JOIN xs01_path e ON d.edge = e.ogc_fid
    ORDER BY d.seq;
END;
$$ LANGUAGE plpgsql STABLE;