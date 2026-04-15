SELECT format(
  'CREATE ROLE rag_owner LOGIN PASSWORD %L',
  :'rag_owner_pass'
)
WHERE NOT EXISTS (
  SELECT 1
  FROM pg_roles
  WHERE rolname = 'rag_owner'
);
\gexec

SELECT format(
  'ALTER ROLE rag_owner WITH LOGIN PASSWORD %L',
  :'rag_owner_pass'
);
\gexec

SELECT format(
  'CREATE ROLE rag_app LOGIN PASSWORD %L',
  :'rag_app_pass'
)
WHERE NOT EXISTS (
  SELECT 1
  FROM pg_roles
  WHERE rolname = 'rag_app'
);
\gexec

SELECT format(
  'ALTER ROLE rag_app WITH LOGIN PASSWORD %L',
  :'rag_app_pass'
);
\gexec

SELECT format(
  'CREATE ROLE rag_ro LOGIN PASSWORD %L',
  :'rag_ro_pass'
)
WHERE NOT EXISTS (
  SELECT 1
  FROM pg_roles
  WHERE rolname = 'rag_ro'
);
\gexec

SELECT format(
  'ALTER ROLE rag_ro WITH LOGIN PASSWORD %L',
  :'rag_ro_pass'
);
\gexec
