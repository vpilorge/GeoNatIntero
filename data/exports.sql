SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
--
SET row_security = off;


CREATE SCHEMA IF NOT EXISTS gn_intero;

SET search_path = gn_intero, pg_catalog;
SET default_tablespace = '';
SET default_with_oids = false;


-- DROP TABLE IF EXISTS gn_intero.cor_exports_roles;
CREATE TABLE cor_exports_roles (
    id_cor_exports_roles SERIAL NOT NULL,
    roles character(255)
    CONSTRAINT cor_exports_roles_pkey PRIMARY KEY (id_cor_exports_roles);
);

-- TODO: t_config_exports GeoNature/issues/282

-- DROP TABLE IF EXISTS gn_intero.t_exports;
CREATE TABLE gn_intero.t_exports (
  id SERIAL NOT NULL,
  label text COLLATE pg_catalog."default" NOT NULL,
  selection text COLLATE pg_catalog."default" NOT NULL,
  CONSTRAINT t_export_pkey1 PRIMARY KEY (id)
)

-- DROP TABLE IF EXISTS gn_intero.t_exports_logs;
-- TODO: id_role
CREATE TABLE gn_intero.t_exports_logs (
    id TIMESTAMP NOT NULL,
    format integer NOT NULL,
    selection text COLLATE pg_catalog."default",
    start date,
    "end" date,
    status numeric DEFAULT '-2'::integer,
    log text COLLATE pg_catalog."default",
    standard integer NOT NULL DEFAULT 0,
    id_export integer,
    CONSTRAINT t_exports_logs_pkey PRIMARY KEY (id),
    CONSTRAINT fk_export_type_selection FOREIGN KEY (id_export)
      REFERENCES gn_intero.t_exports (id) MATCH SIMPLE
      ON UPDATE NO ACTION
      ON DELETE NO ACTION
)

-- TODO: create view backend .. cron job 
CREATE OR REPLACE VIEW gn_intero.v_export WITH (security_barrier='false') AS
  SELECT  export_occtax_sinp."nomCite",
          export_occtax_sinp."dateDebut",
          export_occtax_sinp."dateFin",
          export_occtax_sinp."heureDebut",
          export_occtax_sinp."heureFin",
          export_occtax_sinp."altMax",
          export_occtax_sinp."altMin",
          export_occtax_sinp."cdNom",
          export_occtax_sinp."cdRef"
  FROM pr_occtax.export_occtax_sinp;

CREATE OR REPLACE VIEW gn_intero.v_export_SINP WITH (security_barrier='false') AS
  SELECT  export_occtax_sinp."permId",
          export_occtax_sinp."statObs",
          export_occtax_sinp."nomCite",
          export_occtax_sinp."dateDebut",
          export_occtax_sinp."dateFin",
          export_occtax_sinp."heureDebut",
          export_occtax_sinp."heureFin",
          export_occtax_sinp."altMax",
          export_occtax_sinp."altMin",
          export_occtax_sinp."cdNom",
          export_occtax_sinp."cdRef",
          export_occtax_sinp."versionTAXREF",
          export_occtax_sinp.datedet,
          export_occtax_sinp.comment,
          export_occtax_sinp."dSPublique",
          export_occtax_sinp."jddMetadonneeDEEId",
          export_occtax_sinp."statSource",
          export_occtax_sinp."diffusionNiveauPrecision",
          export_occtax_sinp."idOrigine",
          export_occtax_sinp."jddCode",
          export_occtax_sinp."jddId",
          export_occtax_sinp."refBiblio",
          export_occtax_sinp."obsMeth",
          export_occtax_sinp."ocEtatBio",
          export_occtax_sinp."ocNat",
          export_occtax_sinp."ocSex",
          export_occtax_sinp."ocStade",
          export_occtax_sinp."ocBiogeo",
          export_occtax_sinp."ocStatBio",
          export_occtax_sinp."preuveOui",
          export_occtax_sinp."ocMethDet",
          export_occtax_sinp."preuvNum",
          export_occtax_sinp."preuvNoNum",
          export_occtax_sinp."obsCtx",
          export_occtax_sinp."permIdGrp",
          export_occtax_sinp."methGrp",
          export_occtax_sinp."typGrp",
          export_occtax_sinp."denbrMax",
          export_occtax_sinp."denbrMin",
          export_occtax_sinp."objDenbr",
          export_occtax_sinp."typDenbr",
          export_occtax_sinp."obsId",
          export_occtax_sinp."obsNomOrg",
          export_occtax_sinp."detId",
          export_occtax_sinp."detNomOrg",
          export_occtax_sinp."orgGestDat",
          export_occtax_sinp."WKT",
          export_occtax_sinp."natObjGeo"
  FROM pr_occtax.export_occtax_sinp;


CREATE OR REPLACE VIEW gn_intero.v_export_DwC WITH (security_barrier='false') AS
  SELECT  export_occtax_sinp."permId" AS "OccurrenceID",
          concat(export_occtax_sinp."statObs",' ', export_occtax_sinp."statSource") AS "OccurrenceStatus",
          export_occtax_sinp."nomCite" AS "ScientificName",
          concat(export_occtax_sinp."dateDebut",' ',export_occtax_sinp."heureDebut",' , ', export_occtax_sinp."dateFin",' ', export_occtax_sinp."heureFin") AS "eventDate",
          export_occtax_sinp."altMax" AS "maximumElevationInMeters",
          export_occtax_sinp."altMin" AS "minimumElevationInMeters",
          export_occtax_sinp."cdNom" AS "taxonID",
          export_occtax_sinp.datedet AS "dateIdentified",
          export_occtax_sinp.comment AS "occurrenceRemarks",
          export_occtax_sinp."idOrigine" AS "CatalogNumber",
          export_occtax_sinp."jddCode" AS "CollectionCode",
          export_occtax_sinp."jddId" AS "CollectionId",
          export_occtax_sinp."refBiblio" AS "associatedReferences",
          export_occtax_sinp."ocMethDet" AS "basisOfRecord",
          export_occtax_sinp."denbrMin" AS "Individual Count",
          concat(export_occtax_sinp."obsId",' ', export_occtax_sinp."obsNomOrg") AS "recordedBy",
          export_occtax_sinp."detId" AS "identifiedBy",
          export_occtax_sinp."orgGestDat" AS "InstitutionCode",
          export_occtax_sinp."WKT" AS "footprintWKT"
  FROM pr_occtax.export_occtax_sinp;
