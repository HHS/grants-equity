import datetime

from src.db.models.foreign.attachment import TsynopsisAttachment as TsynopsisAttachmentF
from src.db.models.staging.attachment import TsynopsisAttachment as TsynopsisAttachmentS
from tests.src.db.models.factories import (
    ForeignTsynopsisAttachmentFactory,
    StagingTsynopsisAttachmentFactory, ForeignTopportunityFactory,
)


def test_uploading_attachment_staging(db_session, enable_factory_create, tmp_path):
    att = StagingTsynopsisAttachmentFactory.create(file_lob=b"Testing attachment")
    db_session.commit()
    db_session.expire_all()

    db_att = (
        db_session.query(TsynopsisAttachmentS)
        .filter(TsynopsisAttachmentS.opportunity_id == att.opportunity_id)
        .one_or_none()
    )
    temp_file = tmp_path / "out_file.txt"
    temp_file.write_bytes(db_att.file_lob)
    file_content = temp_file.read_bytes()

    assert file_content == db_att.file_lob


def test_uploading_attachment_foreign(db_session, enable_factory_create, tmp_path):
    ForeignTopportunityFactory.create(
        opportunity_id=1, oppnumber="A-1", cfdas=[], last_upd_date=datetime.datetime(2024, 1, 20, 7, 15, 0)

    )
    att = ForeignTsynopsisAttachmentFactory.create(file_lob=b"Testing saving to db")
    db_session.commit()
    db_session.expire_all()

    db_att = (
        db_session.query(TsynopsisAttachmentF)
        .filter(TsynopsisAttachmentF.opportunity_id == att.opportunity_id)
        .one_or_none()
    )

    temp_file = tmp_path / "out_file.txt"
    temp_file.write_bytes(db_att.file_lob)
    file_content = temp_file.read_bytes()

    assert file_content == db_att.file_lob
