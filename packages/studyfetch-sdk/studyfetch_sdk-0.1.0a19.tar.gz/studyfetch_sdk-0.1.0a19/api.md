# V1

Methods:

- <code title="get /api/v1/test-mongodb">client.v1.<a href="./src/studyfetch_sdk/resources/v1/v1.py">test_mongodb</a>() -> None</code>

## Materials

Types:

```python
from studyfetch_sdk.types.v1 import (
    Content,
    Material,
    MaterialListResponse,
    MaterialBatchCreateResponse,
    MaterialDebugResponse,
    MaterialGetDownloadURLResponse,
    MaterialSearchResponse,
)
```

Methods:

- <code title="post /api/v1/materials">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">create</a>(\*\*<a href="src/studyfetch_sdk/types/v1/material_create_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material.py">Material</a></code>
- <code title="get /api/v1/materials/{id}">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">retrieve</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/material.py">Material</a></code>
- <code title="get /api/v1/materials">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">list</a>(\*\*<a href="src/studyfetch_sdk/types/v1/material_list_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_list_response.py">MaterialListResponse</a></code>
- <code title="delete /api/v1/materials/{id}">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">delete</a>(id) -> None</code>
- <code title="post /api/v1/materials/batch">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">batch_create</a>(\*\*<a href="src/studyfetch_sdk/types/v1/material_batch_create_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_batch_create_response.py">MaterialBatchCreateResponse</a></code>
- <code title="post /api/v1/materials/upload-and-process">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">create_and_process</a>(\*\*<a href="src/studyfetch_sdk/types/v1/material_create_and_process_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material.py">Material</a></code>
- <code title="get /api/v1/materials/{id}/debug">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">debug</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/material_debug_response.py">MaterialDebugResponse</a></code>
- <code title="get /api/v1/materials/{id}/download-url">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">get_download_url</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/material_get_download_url_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_get_download_url_response.py">MaterialGetDownloadURLResponse</a></code>
- <code title="post /api/v1/materials/{id}/move">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">move</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/material_move_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material.py">Material</a></code>
- <code title="post /api/v1/materials/{id}/rename">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">rename</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/material_rename_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material.py">Material</a></code>
- <code title="post /api/v1/materials/{id}/reprocess">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">reprocess</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/material.py">Material</a></code>
- <code title="post /api/v1/materials/search">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">search</a>(\*\*<a href="src/studyfetch_sdk/types/v1/material_search_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_search_response.py">MaterialSearchResponse</a></code>

### Upload

Types:

```python
from studyfetch_sdk.types.v1.materials import Complete, UploadCreatePresignedURLResponse
```

Methods:

- <code title="post /api/v1/materials/upload/complete">client.v1.materials.upload.<a href="./src/studyfetch_sdk/resources/v1/materials/upload.py">complete_upload</a>(\*\*<a href="src/studyfetch_sdk/types/v1/materials/upload_complete_upload_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material.py">Material</a></code>
- <code title="post /api/v1/materials/upload/presigned-url">client.v1.materials.upload.<a href="./src/studyfetch_sdk/resources/v1/materials/upload.py">create_presigned_url</a>(\*\*<a href="src/studyfetch_sdk/types/v1/materials/upload_create_presigned_url_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/materials/upload_create_presigned_url_response.py">UploadCreatePresignedURLResponse</a></code>
- <code title="post /api/v1/materials/upload">client.v1.materials.upload.<a href="./src/studyfetch_sdk/resources/v1/materials/upload.py">upload_file</a>(\*\*<a href="src/studyfetch_sdk/types/v1/materials/upload_upload_file_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material.py">Material</a></code>
- <code title="post /api/v1/materials/upload/file-and-process">client.v1.materials.upload.<a href="./src/studyfetch_sdk/resources/v1/materials/upload.py">upload_file_and_process</a>(\*\*<a href="src/studyfetch_sdk/types/v1/materials/upload_upload_file_and_process_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material.py">Material</a></code>
- <code title="post /api/v1/materials/upload/url">client.v1.materials.upload.<a href="./src/studyfetch_sdk/resources/v1/materials/upload.py">upload_from_url</a>(\*\*<a href="src/studyfetch_sdk/types/v1/materials/upload_upload_from_url_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material.py">Material</a></code>
- <code title="post /api/v1/materials/upload/url-and-process">client.v1.materials.upload.<a href="./src/studyfetch_sdk/resources/v1/materials/upload.py">upload_url_and_process</a>(\*\*<a href="src/studyfetch_sdk/types/v1/materials/upload_upload_url_and_process_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material.py">Material</a></code>

### Bulk

Types:

```python
from studyfetch_sdk.types.v1.materials import BulkMoveResponse
```

Methods:

- <code title="post /api/v1/materials/bulk/move">client.v1.materials.bulk.<a href="./src/studyfetch_sdk/resources/v1/materials/bulk.py">move</a>(\*\*<a href="src/studyfetch_sdk/types/v1/materials/bulk_move_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/materials/bulk_move_response.py">BulkMoveResponse</a></code>

### Test

Types:

```python
from studyfetch_sdk.types.v1.materials import (
    TestPerformOcrResponse,
    TestProcessEpubResponse,
    TestProcessImageResponse,
    TestProcessVideoResponse,
)
```

Methods:

- <code title="post /api/v1/materials/test/ocr">client.v1.materials.test.<a href="./src/studyfetch_sdk/resources/v1/materials/test.py">perform_ocr</a>() -> <a href="./src/studyfetch_sdk/types/v1/materials/test_perform_ocr_response.py">TestPerformOcrResponse</a></code>
- <code title="post /api/v1/materials/test/epub-processing">client.v1.materials.test.<a href="./src/studyfetch_sdk/resources/v1/materials/test.py">process_epub</a>() -> <a href="./src/studyfetch_sdk/types/v1/materials/test_process_epub_response.py">TestProcessEpubResponse</a></code>
- <code title="post /api/v1/materials/test/image-processing">client.v1.materials.test.<a href="./src/studyfetch_sdk/resources/v1/materials/test.py">process_image</a>() -> <a href="./src/studyfetch_sdk/types/v1/materials/test_process_image_response.py">TestProcessImageResponse</a></code>
- <code title="post /api/v1/materials/test/video-processing">client.v1.materials.test.<a href="./src/studyfetch_sdk/resources/v1/materials/test.py">process_video</a>() -> <a href="./src/studyfetch_sdk/types/v1/materials/test_process_video_response.py">TestProcessVideoResponse</a></code>

## Folders

Methods:

- <code title="post /api/v1/folders">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">create</a>(\*\*<a href="src/studyfetch_sdk/types/v1/folder_create_params.py">params</a>) -> None</code>
- <code title="get /api/v1/folders/{id}">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">retrieve</a>(id) -> None</code>
- <code title="patch /api/v1/folders/{id}">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">update</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/folder_update_params.py">params</a>) -> None</code>
- <code title="get /api/v1/folders">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">list</a>(\*\*<a href="src/studyfetch_sdk/types/v1/folder_list_params.py">params</a>) -> None</code>
- <code title="delete /api/v1/folders/{id}">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">delete</a>(id) -> None</code>
- <code title="get /api/v1/folders/tree">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">get_tree</a>() -> None</code>
- <code title="get /api/v1/folders/{id}/materials">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">list_materials</a>(id) -> None</code>
- <code title="patch /api/v1/folders/{id}/move">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">move</a>(id) -> None</code>

## Components

Types:

```python
from studyfetch_sdk.types.v1 import Component, ComponentListResponse, ComponentGenerateEmbedResponse
```

Methods:

- <code title="post /api/v1/components">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">create</a>(\*\*<a href="src/studyfetch_sdk/types/v1/component_create_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/component.py">Component</a></code>
- <code title="get /api/v1/components/{id}">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">retrieve</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/component.py">Component</a></code>
- <code title="patch /api/v1/components/{id}">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">update</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/component_update_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/component.py">Component</a></code>
- <code title="get /api/v1/components">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">list</a>(\*\*<a href="src/studyfetch_sdk/types/v1/component_list_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/component_list_response.py">ComponentListResponse</a></code>
- <code title="delete /api/v1/components/{id}">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">delete</a>(id) -> None</code>
- <code title="post /api/v1/components/{id}/activate">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">activate</a>(id) -> None</code>
- <code title="post /api/v1/components/{id}/deactivate">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">deactivate</a>(id) -> None</code>
- <code title="post /api/v1/components/{id}/embed">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">generate_embed</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/component_generate_embed_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/component_generate_embed_response.py">ComponentGenerateEmbedResponse</a></code>
- <code title="post /api/v1/components/{id}/interact">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">interact</a>(id) -> None</code>

## Usage

Methods:

- <code title="get /api/v1/usage/stats">client.v1.usage.<a href="./src/studyfetch_sdk/resources/v1/usage/usage.py">get_stats</a>(\*\*<a href="src/studyfetch_sdk/types/v1/usage_get_stats_params.py">params</a>) -> None</code>
- <code title="get /api/v1/usage/summary">client.v1.usage.<a href="./src/studyfetch_sdk/resources/v1/usage/usage.py">get_summary</a>(\*\*<a href="src/studyfetch_sdk/types/v1/usage_get_summary_params.py">params</a>) -> None</code>
- <code title="get /api/v1/usage/events">client.v1.usage.<a href="./src/studyfetch_sdk/resources/v1/usage/usage.py">list_events</a>(\*\*<a href="src/studyfetch_sdk/types/v1/usage_list_events_params.py">params</a>) -> None</code>

### Analyst

Types:

```python
from studyfetch_sdk.types.v1.usage import AnalystListChatMessagesResponse
```

Methods:

- <code title="get /api/v1/usage-analyst/test-questions">client.v1.usage.analyst.<a href="./src/studyfetch_sdk/resources/v1/usage/analyst.py">get_test_questions</a>(\*\*<a href="src/studyfetch_sdk/types/v1/usage/analyst_get_test_questions_params.py">params</a>) -> None</code>
- <code title="get /api/v1/usage-analyst/chat-messages">client.v1.usage.analyst.<a href="./src/studyfetch_sdk/resources/v1/usage/analyst.py">list_chat_messages</a>(\*\*<a href="src/studyfetch_sdk/types/v1/usage/analyst_list_chat_messages_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/usage/analyst_list_chat_messages_response.py">AnalystListChatMessagesResponse</a></code>
- <code title="get /api/v1/usage-analyst/events">client.v1.usage.analyst.<a href="./src/studyfetch_sdk/resources/v1/usage/analyst.py">list_events</a>(\*\*<a href="src/studyfetch_sdk/types/v1/usage/analyst_list_events_params.py">params</a>) -> None</code>

## Embed

Methods:

- <code title="get /api/v1/embed/theme">client.v1.embed.<a href="./src/studyfetch_sdk/resources/v1/embed/embed.py">get_theme</a>(\*\*<a href="src/studyfetch_sdk/types/v1/embed_get_theme_params.py">params</a>) -> None</code>
- <code title="get /api/v1/embed/health">client.v1.embed.<a href="./src/studyfetch_sdk/resources/v1/embed/embed.py">health_check</a>() -> None</code>
- <code title="get /api/v1/embed/verify">client.v1.embed.<a href="./src/studyfetch_sdk/resources/v1/embed/embed.py">verify</a>(\*\*<a href="src/studyfetch_sdk/types/v1/embed_verify_params.py">params</a>) -> None</code>

### Component

Methods:

- <code title="get /api/v1/embed/component/{componentId}">client.v1.embed.component.<a href="./src/studyfetch_sdk/resources/v1/embed/component.py">retrieve</a>(component_id, \*\*<a href="src/studyfetch_sdk/types/v1/embed/component_retrieve_params.py">params</a>) -> None</code>
- <code title="post /api/v1/embed/component/{componentId}/interact">client.v1.embed.component.<a href="./src/studyfetch_sdk/resources/v1/embed/component.py">interact</a>(component_id, \*\*<a href="src/studyfetch_sdk/types/v1/embed/component_interact_params.py">params</a>) -> None</code>

## Chat

Types:

```python
from studyfetch_sdk.types.v1 import Interaction
```

Methods:

- <code title="post /api/v1/chat/history">client.v1.chat.<a href="./src/studyfetch_sdk/resources/v1/chat/chat.py">get_history</a>() -> None</code>
- <code title="get /api/v1/chat/session/{sessionId}">client.v1.chat.<a href="./src/studyfetch_sdk/resources/v1/chat/chat.py">get_session</a>(session_id, \*\*<a href="src/studyfetch_sdk/types/v1/chat_get_session_params.py">params</a>) -> None</code>
- <code title="post /api/v1/chat/followups">client.v1.chat.<a href="./src/studyfetch_sdk/resources/v1/chat/chat.py">send_followups</a>() -> None</code>
- <code title="post /api/v1/chat/message">client.v1.chat.<a href="./src/studyfetch_sdk/resources/v1/chat/chat.py">send_message</a>(\*\*<a href="src/studyfetch_sdk/types/v1/chat_send_message_params.py">params</a>) -> None</code>
- <code title="post /api/v1/chat/stream">client.v1.chat.<a href="./src/studyfetch_sdk/resources/v1/chat/chat.py">stream</a>(\*\*<a href="src/studyfetch_sdk/types/v1/chat_stream_params.py">params</a>) -> None</code>

### Sessions

Methods:

- <code title="post /api/v1/chat/sessions/create">client.v1.chat.sessions.<a href="./src/studyfetch_sdk/resources/v1/chat/sessions.py">create</a>() -> None</code>
- <code title="get /api/v1/chat/sessions/{userId}">client.v1.chat.sessions.<a href="./src/studyfetch_sdk/resources/v1/chat/sessions.py">retrieve</a>(user_id, \*\*<a href="src/studyfetch_sdk/types/v1/chat/session_retrieve_params.py">params</a>) -> None</code>

### Test

Methods:

- <code title="post /api/v1/chat/test/image-citation">client.v1.chat.test.<a href="./src/studyfetch_sdk/resources/v1/chat/test.py">cite_image</a>() -> None</code>
- <code title="post /api/v1/chat/test/image">client.v1.chat.test.<a href="./src/studyfetch_sdk/resources/v1/chat/test.py">upload_image</a>() -> None</code>

## Tests

Methods:

- <code title="post /api/v1/tests/create">client.v1.tests.<a href="./src/studyfetch_sdk/resources/v1/tests/tests.py">create</a>(\*\*<a href="src/studyfetch_sdk/types/v1/test_create_params.py">params</a>) -> None</code>
- <code title="get /api/v1/tests/{testId}">client.v1.tests.<a href="./src/studyfetch_sdk/resources/v1/tests/tests.py">retrieve</a>(test_id) -> None</code>
- <code title="get /api/v1/tests/{testId}/results">client.v1.tests.<a href="./src/studyfetch_sdk/resources/v1/tests/tests.py">get_results</a>(test_id) -> None</code>
- <code title="post /api/v1/tests/{testId}/retake">client.v1.tests.<a href="./src/studyfetch_sdk/resources/v1/tests/tests.py">retake</a>(test_id, \*\*<a href="src/studyfetch_sdk/types/v1/test_retake_params.py">params</a>) -> None</code>
- <code title="post /api/v1/tests/{testId}/submit">client.v1.tests.<a href="./src/studyfetch_sdk/resources/v1/tests/tests.py">submit</a>(test_id, \*\*<a href="src/studyfetch_sdk/types/v1/test_submit_params.py">params</a>) -> None</code>
- <code title="post /api/v1/tests/{testId}/submit-answer">client.v1.tests.<a href="./src/studyfetch_sdk/resources/v1/tests/tests.py">submit_answer</a>(test_id, \*\*<a href="src/studyfetch_sdk/types/v1/test_submit_answer_params.py">params</a>) -> None</code>

### Component

Methods:

- <code title="post /api/v1/tests/component/{componentId}/list">client.v1.tests.component.<a href="./src/studyfetch_sdk/resources/v1/tests/component.py">list</a>(component_id) -> None</code>

## AudioRecaps

Methods:

- <code title="post /api/v1/audio-recaps/create">client.v1.audio_recaps.<a href="./src/studyfetch_sdk/resources/v1/audio_recaps/audio_recaps.py">create</a>() -> None</code>
- <code title="get /api/v1/audio-recaps/{recapId}/get">client.v1.audio_recaps.<a href="./src/studyfetch_sdk/resources/v1/audio_recaps/audio_recaps.py">retrieve</a>(recap_id) -> None</code>
- <code title="post /api/v1/audio-recaps/{recapId}/ask-question">client.v1.audio_recaps.<a href="./src/studyfetch_sdk/resources/v1/audio_recaps/audio_recaps.py">ask_question</a>(recap_id) -> None</code>

### Sections

Methods:

- <code title="get /api/v1/audio-recaps/{recapId}/sections/{sectionId}">client.v1.audio_recaps.sections.<a href="./src/studyfetch_sdk/resources/v1/audio_recaps/sections.py">retrieve</a>(section_id, \*, recap_id) -> None</code>
- <code title="get /api/v1/audio-recaps/{recapId}/sections">client.v1.audio_recaps.sections.<a href="./src/studyfetch_sdk/resources/v1/audio_recaps/sections.py">list</a>(recap_id) -> None</code>

## Flashcards

Types:

```python
from studyfetch_sdk.types.v1 import (
    FlashcardBatchProcessResponse,
    FlashcardGetAlgorithmResponse,
    FlashcardGetTypesResponse,
)
```

Methods:

- <code title="post /api/v1/flashcards/{componentId}/batch">client.v1.flashcards.<a href="./src/studyfetch_sdk/resources/v1/flashcards.py">batch_process</a>(component_id, \*\*<a href="src/studyfetch_sdk/types/v1/flashcard_batch_process_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/flashcard_batch_process_response.py">FlashcardBatchProcessResponse</a></code>
- <code title="get /api/v1/flashcards/algorithm">client.v1.flashcards.<a href="./src/studyfetch_sdk/resources/v1/flashcards.py">get_algorithm</a>() -> <a href="./src/studyfetch_sdk/types/v1/flashcard_get_algorithm_response.py">FlashcardGetAlgorithmResponse</a></code>
- <code title="get /api/v1/flashcards/{componentId}/all">client.v1.flashcards.<a href="./src/studyfetch_sdk/resources/v1/flashcards.py">get_all</a>(component_id, \*\*<a href="src/studyfetch_sdk/types/v1/flashcard_get_all_params.py">params</a>) -> None</code>
- <code title="get /api/v1/flashcards/{componentId}/due">client.v1.flashcards.<a href="./src/studyfetch_sdk/resources/v1/flashcards.py">get_due</a>(component_id, \*\*<a href="src/studyfetch_sdk/types/v1/flashcard_get_due_params.py">params</a>) -> None</code>
- <code title="get /api/v1/flashcards/{componentId}/stats">client.v1.flashcards.<a href="./src/studyfetch_sdk/resources/v1/flashcards.py">get_stats</a>(component_id, \*\*<a href="src/studyfetch_sdk/types/v1/flashcard_get_stats_params.py">params</a>) -> None</code>
- <code title="get /api/v1/flashcards/types">client.v1.flashcards.<a href="./src/studyfetch_sdk/resources/v1/flashcards.py">get_types</a>() -> <a href="./src/studyfetch_sdk/types/v1/flashcard_get_types_response.py">FlashcardGetTypesResponse</a></code>
- <code title="post /api/v1/flashcards/{componentId}/rate">client.v1.flashcards.<a href="./src/studyfetch_sdk/resources/v1/flashcards.py">rate</a>(component_id, \*\*<a href="src/studyfetch_sdk/types/v1/flashcard_rate_params.py">params</a>) -> None</code>

## Scenarios

Types:

```python
from studyfetch_sdk.types.v1 import Scenario, UpdateScenario
```

Methods:

- <code title="post /api/v1/scenarios">client.v1.scenarios.<a href="./src/studyfetch_sdk/resources/v1/scenarios/scenarios.py">create</a>(\*\*<a href="src/studyfetch_sdk/types/v1/scenario_create_params.py">params</a>) -> None</code>
- <code title="get /api/v1/scenarios/{id}">client.v1.scenarios.<a href="./src/studyfetch_sdk/resources/v1/scenarios/scenarios.py">retrieve</a>(id) -> None</code>
- <code title="put /api/v1/scenarios/{id}">client.v1.scenarios.<a href="./src/studyfetch_sdk/resources/v1/scenarios/scenarios.py">update</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/scenario_update_params.py">params</a>) -> None</code>
- <code title="get /api/v1/scenarios">client.v1.scenarios.<a href="./src/studyfetch_sdk/resources/v1/scenarios/scenarios.py">list</a>() -> None</code>
- <code title="delete /api/v1/scenarios/{id}">client.v1.scenarios.<a href="./src/studyfetch_sdk/resources/v1/scenarios/scenarios.py">delete</a>(id) -> None</code>
- <code title="get /api/v1/scenarios/{id}/stats">client.v1.scenarios.<a href="./src/studyfetch_sdk/resources/v1/scenarios/scenarios.py">get_stats</a>(id) -> None</code>
- <code title="post /api/v1/scenarios/{id}/submit">client.v1.scenarios.<a href="./src/studyfetch_sdk/resources/v1/scenarios/scenarios.py">submit_answer</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/scenario_submit_answer_params.py">params</a>) -> None</code>

### Component

Methods:

- <code title="get /api/v1/scenarios/component/{componentId}">client.v1.scenarios.component.<a href="./src/studyfetch_sdk/resources/v1/scenarios/component.py">retrieve</a>(component_id) -> None</code>
- <code title="put /api/v1/scenarios/component/{componentId}">client.v1.scenarios.component.<a href="./src/studyfetch_sdk/resources/v1/scenarios/component.py">update</a>(component_id, \*\*<a href="src/studyfetch_sdk/types/v1/scenarios/component_update_params.py">params</a>) -> None</code>
- <code title="delete /api/v1/scenarios/component/{componentId}">client.v1.scenarios.component.<a href="./src/studyfetch_sdk/resources/v1/scenarios/component.py">delete</a>(component_id) -> None</code>

### Sessions

Methods:

- <code title="put /api/v1/scenarios/sessions/{sessionId}/complete">client.v1.scenarios.sessions.<a href="./src/studyfetch_sdk/resources/v1/scenarios/sessions.py">complete</a>(session_id) -> None</code>
- <code title="post /api/v1/scenarios/{id}/sessions/start">client.v1.scenarios.sessions.<a href="./src/studyfetch_sdk/resources/v1/scenarios/sessions.py">start</a>(id) -> None</code>

### Submissions

#### User

Methods:

- <code title="get /api/v1/scenarios/submissions/user">client.v1.scenarios.submissions.user.<a href="./src/studyfetch_sdk/resources/v1/scenarios/submissions/user.py">get_all</a>() -> None</code>
- <code title="get /api/v1/scenarios/{id}/submissions/user">client.v1.scenarios.submissions.user.<a href="./src/studyfetch_sdk/resources/v1/scenarios/submissions/user.py">get_by_scenario</a>(id) -> None</code>

## Explainers

Methods:

- <code title="post /api/v1/explainers/create">client.v1.explainers.<a href="./src/studyfetch_sdk/resources/v1/explainers.py">create</a>(\*\*<a href="src/studyfetch_sdk/types/v1/explainer_create_params.py">params</a>) -> None</code>
- <code title="get /api/v1/explainers/component/{componentId}">client.v1.explainers.<a href="./src/studyfetch_sdk/resources/v1/explainers.py">retrieve</a>(component_id) -> None</code>
- <code title="post /api/v1/explainers/webhook">client.v1.explainers.<a href="./src/studyfetch_sdk/resources/v1/explainers.py">handle_webhook</a>(\*\*<a href="src/studyfetch_sdk/types/v1/explainer_handle_webhook_params.py">params</a>) -> None</code>

## Upload

### Component

Types:

```python
from studyfetch_sdk.types.v1.upload import (
    FileUploadResponse,
    ComponentCompleteUploadResponse,
    ComponentGetPresignedURLResponse,
)
```

Methods:

- <code title="post /api/v1/upload/component/{componentId}/complete">client.v1.upload.component.<a href="./src/studyfetch_sdk/resources/v1/upload/component.py">complete_upload</a>(component_id, \*\*<a href="src/studyfetch_sdk/types/v1/upload/component_complete_upload_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/upload/component_complete_upload_response.py">ComponentCompleteUploadResponse</a></code>
- <code title="post /api/v1/upload/component/{componentId}/presigned-url">client.v1.upload.component.<a href="./src/studyfetch_sdk/resources/v1/upload/component.py">get_presigned_url</a>(component_id, \*\*<a href="src/studyfetch_sdk/types/v1/upload/component_get_presigned_url_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/upload/component_get_presigned_url_response.py">ComponentGetPresignedURLResponse</a></code>
- <code title="post /api/v1/upload/component/{componentId}/file">client.v1.upload.component.<a href="./src/studyfetch_sdk/resources/v1/upload/component.py">upload_file</a>(component_id, \*\*<a href="src/studyfetch_sdk/types/v1/upload/component_upload_file_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/upload/file_upload_response.py">FileUploadResponse</a></code>
- <code title="post /api/v1/upload/component/{componentId}/url">client.v1.upload.component.<a href="./src/studyfetch_sdk/resources/v1/upload/component.py">upload_url</a>(component_id, \*\*<a href="src/studyfetch_sdk/types/v1/upload/component_upload_url_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/upload/file_upload_response.py">FileUploadResponse</a></code>

## AssignmentGrader

Types:

```python
from studyfetch_sdk.types.v1 import AssignmentGraderResponse, AssignmentGraderGetAllResponse
```

Methods:

- <code title="post /api/v1/assignment-grader/create">client.v1.assignment_grader.<a href="./src/studyfetch_sdk/resources/v1/assignment_grader.py">create</a>(\*\*<a href="src/studyfetch_sdk/types/v1/assignment_grader_create_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/assignment_grader_response.py">AssignmentGraderResponse</a></code>
- <code title="delete /api/v1/assignment-grader/delete/{id}">client.v1.assignment_grader.<a href="./src/studyfetch_sdk/resources/v1/assignment_grader.py">delete</a>(id) -> None</code>
- <code title="get /api/v1/assignment-grader/get">client.v1.assignment_grader.<a href="./src/studyfetch_sdk/resources/v1/assignment_grader.py">get_all</a>() -> <a href="./src/studyfetch_sdk/types/v1/assignment_grader_get_all_response.py">AssignmentGraderGetAllResponse</a></code>
- <code title="get /api/v1/assignment-grader/get/{id}">client.v1.assignment_grader.<a href="./src/studyfetch_sdk/resources/v1/assignment_grader.py">get_by_id</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/assignment_grader_response.py">AssignmentGraderResponse</a></code>

## DataAnalyst

Methods:

- <code title="post /api/v1/data-analyst/history">client.v1.data_analyst.<a href="./src/studyfetch_sdk/resources/v1/data_analyst/data_analyst.py">get_history</a>() -> None</code>
- <code title="get /api/v1/data-analyst/session/{sessionId}">client.v1.data_analyst.<a href="./src/studyfetch_sdk/resources/v1/data_analyst/data_analyst.py">retrieve_session</a>(session_id, \*\*<a href="src/studyfetch_sdk/types/v1/data_analyst_retrieve_session_params.py">params</a>) -> None</code>
- <code title="post /api/v1/data-analyst/followups">client.v1.data_analyst.<a href="./src/studyfetch_sdk/resources/v1/data_analyst/data_analyst.py">send_followups</a>() -> None</code>
- <code title="post /api/v1/data-analyst/message">client.v1.data_analyst.<a href="./src/studyfetch_sdk/resources/v1/data_analyst/data_analyst.py">send_message</a>(\*\*<a href="src/studyfetch_sdk/types/v1/data_analyst_send_message_params.py">params</a>) -> None</code>
- <code title="post /api/v1/data-analyst/stream">client.v1.data_analyst.<a href="./src/studyfetch_sdk/resources/v1/data_analyst/data_analyst.py">stream</a>(\*\*<a href="src/studyfetch_sdk/types/v1/data_analyst_stream_params.py">params</a>) -> None</code>

### Sessions

Methods:

- <code title="post /api/v1/data-analyst/sessions/create">client.v1.data_analyst.sessions.<a href="./src/studyfetch_sdk/resources/v1/data_analyst/sessions.py">create</a>() -> None</code>
- <code title="get /api/v1/data-analyst/sessions/{userId}">client.v1.data_analyst.sessions.<a href="./src/studyfetch_sdk/resources/v1/data_analyst/sessions.py">retrieve</a>(user_id, \*\*<a href="src/studyfetch_sdk/types/v1/data_analyst/session_retrieve_params.py">params</a>) -> None</code>

### Test

Methods:

- <code title="post /api/v1/data-analyst/test/image">client.v1.data_analyst.test.<a href="./src/studyfetch_sdk/resources/v1/data_analyst/test.py">upload_image</a>() -> None</code>
- <code title="post /api/v1/data-analyst/test/image-citation">client.v1.data_analyst.test.<a href="./src/studyfetch_sdk/resources/v1/data_analyst/test.py">upload_image_citation</a>() -> None</code>
