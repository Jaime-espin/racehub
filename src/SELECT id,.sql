SELECT id,
       nombre,
       deporte,
       fecha,
       localizacion,
       distancia_resumen,
       url_oficial,
       estado_inscripcion
FROM public.carreras
LIMIT 1000;