{% macro maxcompute__concat(fields) -%}
    concat({{ fields|join(', ') }})
{%- endmacro %}
