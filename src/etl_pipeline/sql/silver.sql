create schema if not exists silver;

create or replace table silver.course
as
select
    id::bigint as course_id,
    certificate_id::varchar as certificate_id,
    title::varchar as title,
    published_title::varchar as slug,
    url::varchar as url,
    case
    when 'Ligency' in instructor_title then 'Ed Donner'
    when '|' in instructor_title then trim(string_split(instructor_title, '|')[1])
    when '(' in instructor_title then trim(string_split(instructor_title, '(')[1])
    when ',' in instructor_title then trim(string_split(instructor_title, ',')[1])
    when 'by' in instructor_title then trim(string_split(instructor_title, 'by')[2])
    else trim(instructor_title) end as instructor,
    language::varchar as language,
    is_practice_test_course::boolean as is_practice_test,
    is_paid::boolean as is_paid
from bronze.course;

create or replace table silver.certificate
as
select
    certificate_id::varchar as certificate_id,
    reference_number::char(4) as reference,
    owner::varchar as owner,
    title::varchar as certificate_title,
    instructors::varchar as certificate_instructor,
    course_length::decimal(10,1) as course_length,
    case
    when 'Sept.' in course_end
        then strptime(replace(replace(course_end, 'Sept.', 'Sep'), ', ', ','), '%b %-d,%Y')::date
    when '.' in course_end
        then strptime(replace(replace(course_end, '.', ''), ', ', ','), '%b %-d,%Y')::date
    else
        strptime(replace(course_end, ', ', ','), '%B %-d,%Y')::date end as course_end
from bronze.certificate;
