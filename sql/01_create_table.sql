CREATE DATABASE nhs_ae;
USE nhs_ae;
CREATE TABLE ae_performance (
    period              VARCHAR(30),
    org_code            VARCHAR(20),
    parent_org          VARCHAR(100),
    org_name            VARCHAR(150),
    att_type1           INT,
    att_type2           INT,
    att_other           INT,
    att_booked_type1    INT,
    att_booked_type2    INT,
    att_booked_other    INT,
    over4hr_type1       INT,
    over4hr_type2       INT,
    over4hr_other       INT,
    over4hr_booked_type1 INT,
    over4hr_booked_type2 INT,
    over4hr_booked_other INT,
    wait_4to12hr_dta    INT,
    wait_12plushr_dta   INT,
    emerg_admit_type1   INT,
    emerg_admit_type2   INT,
    emerg_admit_other   INT,
    other_emerg_admit   INT,
    period_clean        VARCHAR(30),
    month_date          DATE
);