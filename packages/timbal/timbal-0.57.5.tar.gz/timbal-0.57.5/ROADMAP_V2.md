

List of tasks to do before moving to core v2:

- Make dump async
- Remove context from dump params
- Separate File.persist from File.serialize
- Make File.persist async
- upload_file() timbal tool
- File.persist should use upload_file()
- Remove context from state savers methods
- Centralize stuff inside TimbalPlatformSaver.put()
- Modify create_model_from_argspec to accept pydantic fields (not just timbal wrapper)
- Add update_usage() to track usage via the run context
