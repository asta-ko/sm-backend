from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        # NOTE: The previous migration probably looks different for you, so
        # modify this.
        ('cases', '0018_auto_20191209_2000'),
    ]

    migration = '''
        CREATE TRIGGER text_search_update BEFORE INSERT OR UPDATE
        ON cases_case FOR EACH ROW EXECUTE FUNCTION
        tsvector_update_trigger(text_search, 'pg_catalog.russian', result_text);

        -- Force triggers to run and populate the text_search column.
        UPDATE cases_case set ID = ID;
    '''

    reverse_migration = '''
        DROP TRIGGER content_search ON case;
    '''

    operations = [
        migrations.RunSQL(migration, reverse_migration)
    ]
