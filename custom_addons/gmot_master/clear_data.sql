delete from gmot_ot_employee;
delete from gmot_ot;
delete from gmot_employee_salary;
update gmleave_employee set effective_date=null, salary=null;
commit;
