alter table Author
add qid varchar;

alter table Author
add date_of_birth_wiki date;

alter table Author
add date_of_death_wiki date;

alter table Author
add place_of_birth_wiki varchar;

alter table Author
add place_of_death_wiki varchar;

alter table Author
add gender varchar;

alter table Book
add qid varchar;