
PRAGMA foreign_keys=ON;
CREATE TABLE sources (
 source_id TEXT PRIMARY KEY, title TEXT NOT NULL, doi TEXT, pmid TEXT,
 url TEXT NOT NULL, source_type TEXT NOT NULL, inspected_scope TEXT NOT NULL,
 accessed_date TEXT NOT NULL, notes TEXT
);
CREATE TABLE variants (
 variant_id TEXT PRIMARY KEY, label TEXT NOT NULL, protein_species TEXT NOT NULL,
 taxon_id INTEGER NOT NULL, mutations_as_reported TEXT,
 background_as_reported TEXT NOT NULL, reference_accession TEXT,
 reference_sequence_version TEXT, sequence_sha256 TEXT,
 identity_status TEXT NOT NULL CHECK(identity_status IN ('sequence_verified','study_scoped','unresolved')),
 source_id TEXT REFERENCES sources, notes TEXT
);
CREATE TABLE compounds (
 compound_id TEXT PRIMARY KEY, name TEXT NOT NULL, chemical_class TEXT,
 linkage TEXT, inchikey TEXT, smiles TEXT, identity_status TEXT NOT NULL,
 identity_source_id TEXT REFERENCES sources, notes TEXT
);
CREATE TABLE endpoints (
 endpoint_id TEXT PRIMARY KEY, name TEXT NOT NULL, definition TEXT NOT NULL
);
CREATE TABLE claims (
 claim_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources,
 variant_id TEXT NOT NULL REFERENCES variants,
 endpoint_id TEXT NOT NULL REFERENCES endpoints,
 treatment_kind TEXT NOT NULL CHECK(treatment_kind IN ('baseline','single','combination')),
 relation TEXT NOT NULL, comparator_as_reported TEXT,
 summary TEXT NOT NULL, locator TEXT NOT NULL,
 evidence_scope TEXT NOT NULL CHECK(evidence_scope IN ('abstract','figure_caption','full_text','supplement')),
 review_status TEXT NOT NULL CHECK(review_status IN ('source_checked','human_reviewed','disputed')),
 notes TEXT
);
CREATE TABLE claim_compounds (
 claim_id TEXT NOT NULL REFERENCES claims, compound_id TEXT NOT NULL REFERENCES compounds,
 role TEXT NOT NULL, PRIMARY KEY(claim_id,compound_id)
);
CREATE TABLE contexts (
 context_id TEXT PRIMARY KEY, host_species TEXT, cell_line TEXT,
 endogenous_sting_status TEXT, expression_mode TEXT, construct_region TEXT,
 tag TEXT, delivery_method TEXT, genotype_zygosity TEXT,
 additional_context_json TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE experiments (
 experiment_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources,
 variant_id TEXT NOT NULL REFERENCES variants, context_id TEXT NOT NULL REFERENCES contexts,
 assay TEXT NOT NULL, treatment_kind TEXT NOT NULL
 CHECK(treatment_kind IN ('baseline','single','combination')),
 vehicle TEXT, time_value REAL, time_unit TEXT, time_status TEXT NOT NULL,
 comparator_experiment_id TEXT REFERENCES experiments,
 study_experiment_label TEXT NOT NULL, independent_dataset_id TEXT,
 biological_replicates INTEGER, technical_replicates INTEGER,
 review_status TEXT NOT NULL, notes TEXT
);
CREATE TABLE treatments (
 experiment_id TEXT NOT NULL REFERENCES experiments,
 compound_id TEXT NOT NULL REFERENCES compounds, role TEXT NOT NULL,
 dose_value REAL, dose_upper REAL, dose_unit TEXT, dose_relation TEXT,
 dose_status TEXT NOT NULL, start_time_value REAL, start_time_unit TEXT,
 formulation TEXT, route TEXT, PRIMARY KEY(experiment_id,compound_id,role)
);
CREATE TABLE measurements (
 measurement_id TEXT PRIMARY KEY, experiment_id TEXT NOT NULL REFERENCES experiments,
 endpoint_id TEXT NOT NULL REFERENCES endpoints, metric TEXT NOT NULL,
 value_numeric REAL, value_upper REAL, value_as_reported TEXT,
 relation TEXT, unit TEXT, qualitative_result TEXT,
 normalization TEXT, uncertainty_type TEXT, uncertainty_value REAL,
 sample_size INTEGER, sample_size_unit TEXT, p_value_text TEXT,
 significance_as_reported TEXT, extraction_method TEXT NOT NULL,
 missing_reason TEXT, locator TEXT NOT NULL, review_status TEXT NOT NULL,
 notes TEXT,
 CHECK(value_numeric IS NOT NULL OR qualitative_result IS NOT NULL OR missing_reason IS NOT NULL),
 CHECK(value_numeric IS NULL OR unit IS NOT NULL)
);
CREATE TABLE structures (
 structure_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources,
 variant_id TEXT REFERENCES variants, protein_species TEXT NOT NULL,
 construct_as_reported TEXT, method TEXT NOT NULL, resolution_A REAL,
 assembly_as_reported TEXT, state_as_reported TEXT, sequence_mapping_status TEXT NOT NULL,
 locator TEXT NOT NULL, notes TEXT
);
CREATE TABLE structure_compounds (
 structure_id TEXT NOT NULL REFERENCES structures,
 compound_id TEXT NOT NULL REFERENCES compounds, pdb_component_id TEXT NOT NULL,
 PRIMARY KEY(structure_id,compound_id)
);
CREATE TABLE field_provenance (
 provenance_id TEXT PRIMARY KEY, record_table TEXT NOT NULL,
 record_id TEXT NOT NULL, field_name TEXT NOT NULL,
 source_id TEXT NOT NULL REFERENCES sources, locator TEXT NOT NULL,
 evidence_kind TEXT NOT NULL CHECK(evidence_kind IN ('reported','derived','hypothesis')),
 derivation TEXT, review_status TEXT NOT NULL
);
CREATE TABLE collection_queue (
 queue_id TEXT PRIMARY KEY, priority INTEGER NOT NULL,
 variant_query TEXT NOT NULL, compound_query TEXT NOT NULL,
 endpoint_query TEXT NOT NULL, search_query TEXT NOT NULL,
 search_state TEXT NOT NULL, rationale TEXT NOT NULL, search_log TEXT
);
CREATE VIEW v_claim_crosslinks AS
 SELECT k.claim_id,v.label AS variant,v.protein_species,v.background_as_reported,
 v.identity_status AS variant_identity,k.treatment_kind,
 COALESCE((SELECT group_concat(name,' + ') FROM
   (SELECT c.name FROM claim_compounds x JOIN compounds c USING(compound_id)
    WHERE x.claim_id=k.claim_id ORDER BY c.name)),'[no exogenous ligand]') AS compounds,
 p.name AS endpoint,k.relation,k.comparator_as_reported,k.summary,
 k.evidence_scope,k.locator,k.review_status,s.doi,s.url
 FROM claims k JOIN variants v USING(variant_id)
 JOIN endpoints p USING(endpoint_id) JOIN sources s USING(source_id);
CREATE VIEW v_measurement_crosslinks AS
 SELECT m.measurement_id,e.experiment_id,v.variant_id,v.label AS variant,
 v.protein_species,ctx.host_species,ctx.cell_line,e.assay,e.treatment_kind,
 (SELECT group_concat(c.name,' + ') FROM treatments t JOIN compounds c USING(compound_id)
  WHERE t.experiment_id=e.experiment_id) AS compounds,
 p.name AS endpoint,m.metric,m.value_numeric,m.value_upper,m.unit,
 m.qualitative_result,e.time_value,e.time_unit,m.normalization,
 e.comparator_experiment_id,m.review_status,m.locator,s.doi,s.url
 FROM measurements m JOIN experiments e USING(experiment_id)
 JOIN variants v USING(variant_id) JOIN contexts ctx USING(context_id)
 JOIN endpoints p USING(endpoint_id) JOIN sources s USING(source_id);
CREATE INDEX idx_claim_variant ON claims(variant_id,endpoint_id);
CREATE INDEX idx_measurement_endpoint ON measurements(endpoint_id,metric);
