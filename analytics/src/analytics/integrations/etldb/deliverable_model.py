from sqlalchemy import text

import pandas

from analytics.datasets.etl_dataset import EtlEntityType as entity
from analytics.integrations.etldb.etldb import EtlChangeType, EtlDb

class EtlDeliverableModel(EtlDb):

    def syncDeliverable(self, deliverable_df: pandas.DataFrame, ghid_map: dict) -> (int, EtlChangeType):
        
        # initialize return value
        change_type = EtlChangeType.NONE

        # get cursor to keep open across transactions
        cursor = self.connection()

        # insert dimensions
        deliverable_id = self._insertDimensions(cursor, deliverable_df)
        if deliverable_id is not None:
            change_type = EtlChangeType.INSERT

        # if insert failed, select and update
        if deliverable_id is None:
            deliverable_id, change_type = self._updateDimensions(cursor, deliverable_df)

        # insert facts 
        if deliverable_id is not None:
            map_id = self._insertFacts(cursor, deliverable_id, deliverable_df, ghid_map)

        # commit
        #self.commit(cursor)

        return deliverable_id, change_type


    def _insertDimensions(self, cursor, deliverable_df: pandas.DataFrame) -> int:

        # get values needed for sql statement
        insert_values = {
            'ghid': deliverable_df['deliverable_ghid'],
            'title': deliverable_df['deliverable_title'],
            'pillar': deliverable_df['deliverable_pillar'],
        }
        new_row_id = None

        # insert into dimension table: deliverable
        insert_sql = f"insert into gh_deliverable(ghid, title, pillar) values (:ghid, :title, :pillar) on conflict(ghid) do nothing returning id"
        result = cursor.execute(text(insert_sql), insert_values)
        row = result.fetchone()
        if row:
            new_row_id = row[0]

        # commit
        self.commit(cursor)

        return new_row_id


    def _insertFacts(self, cursor, deliverable_id: int, deliverable_df: pandas.DataFrame, ghid_map: dict) -> int:

        # get values needed for sql statement
        insert_values = {
            'deliverable_id': deliverable_id,
            'quad_id': ghid_map[entity.QUAD].get(deliverable_df['quad_ghid']),
        }
        new_row_id = None

        # insert into fact table: deliverable_quad_map
        insert_sql = f"insert into gh_deliverable_quad_map(deliverable_id, quad_id, d_effective) values (:deliverable_id, :quad_id, '{self.effective_date}') on conflict(deliverable_id, d_effective) do update set (quad_id, t_modified) = (:quad_id, current_timestamp) returning id"
        result = cursor.execute(text(insert_sql), insert_values)
        row = result.fetchone()
        if row:
            new_row_id = row[0]

        # commit
        self.commit(cursor)

        return new_row_id


    def _updateDimensions(self, cursor, deliverable_df: pandas.DataFrame) -> (int, EtlChangeType):

        # initialize return value
        change_type = EtlChangeType.NONE

        # get values needed for sql statement
        ghid = deliverable_df['deliverable_ghid']
        new_title = deliverable_df['deliverable_title']
        new_pillar = deliverable_df['deliverable_pillar']
        new_values = (new_title, new_pillar)

        # select
        select_sql = f"select id, title, pillar from gh_deliverable where ghid = '{ghid}'"
        result = cursor.execute(text(select_sql),)
        deliverable_id, old_title, old_pillar = result.fetchone()
        old_values = (old_title, old_pillar)

        # compare
        if deliverable_id is not None:
            if (new_values != old_values):
                change_type = EtlChangeType.UPDATE
                update_sql = f"update gh_deliverable set title = :new_title, pillar = :new_pillar, t_modified = current_timestamp where id = :deliverable_id"
                update_values = {
                    'new_title': new_title,
                    'new_pillar': new_pillar,
                    'deliverable_id': deliverable_id,
                }
                result = cursor.execute(text(update_sql), update_values)
                self.commit(cursor)

        return deliverable_id, change_type

