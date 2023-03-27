# hereswhy-ingestor

This is the replacement (v2) for threads-ingestor. With recent and upcoming changes to the Twitter API, this upgrade removes the dependency to the API altogether in place of snscrape.

# Some random notes:

# Ways to optimize ingestion in the future

Currently, the ingestor runtime is acceptable. However, there are a few ways that it can be optimized, if ever need be:

- Bulk upsert optimization: In order to perform upserts, the ingestor currently processes db writes one at a time due to sqlalchemy's lack of native bulk upsert. Here are a couple implementaions of bulk upsert using sqlalchemy:

  1. query db before saving to find existing objects. Split them into bulk_saves and bulk_updates
  2. bulk_save_mappings https://stackoverflow.com/a/67200889/9090347

- multiprocessing when building entities?

# Media id generation

- The default value for media.id is set to gen_random_uuid() in postgres. However, this is not generating random random uuids in the insert statement. A work around for this was to generate the uuids within the injestor itself. This is seemingly safe
