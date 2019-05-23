select
	 qid,
	 shortname,
	 date_of_birth,
	 date_of_birth_wiki
  from Author 
  where date_of_birth not null
  order by fan_count desc


--Количество заполненных данных
select
	 count(*)
  from Author 
  where date_of_birth not null 
    and date_of_birth_wiki not null
  order by fan_count desc

  