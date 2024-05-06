"""
Write from Flask app
to GCS bucket
"""

from google.cloud import storage
from google.oauth2 import service_account
import datetime
import pandas as pd


class GcsConnection:
    """
    creating class to write RSVP data
    from the Flask app to GCS
    """

    def __init__(
        self,
        service_accnt: service_account.Credentials,
        gcs_bucket: str,
    ) -> None:

        self.gcp_service_accnt = service_accnt
        self.gcs_bucket = gcs_bucket

    def write_to_gcs(self, rsvp: pd.DataFrame) -> None:
        today = datetime.date.today()
        write_date = str(today)
        datetime_hash = hash(datetime.datetime.now())

        storage_client = storage.Client(credentials=self.gcp_service_accnt)
        bucket = storage_client.get_bucket(self.gcs_bucket)

        blob_name = 'rsvps/rsvp_' + \
            str(datetime_hash) + '_' + write_date + '.csv'

        bucket\
            .blob(blob_name)\
            .upload_from_string(rsvp.to_csv(index=False), 'text/csv')

        print('Writing data to GCS location:',
              self.gcs_bucket + '/' + blob_name)
        print('Number of rows:', rsvp.shape[0])
        pass


"""
gcs_connection = WriteToGCS(service_accnt=gcp_service_accnt,
    gcs_bucket='website-responses/rsvps')
gcs_connection.write_to_gcs(rsvp=rsvp_df)
"""
