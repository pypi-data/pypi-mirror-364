<gsl-template type="spec" trace_id="YYYYMMDDTHHMMSS±HHMM">
<gsl-header>

# Grit Labs Spec Template
</gsl-header>

<gsl-block>
<gsl-label> 

## Title:
</gsl-label>
<gsl-title> 

Specify avatar upload interface
</gsl-title>

<gsl-label>

## Purpose:
</gsl-label>
<gsl-description>

Define the interface contract and input/output rules for avatar upload functionality.

</gsl-description>

<gsl-label>

## Inputs:
</gsl-label>
<gsl-description>

- File: binary (JPEG, PNG, WebP)  
- Size: max 5MB  
- Endpoint: `POST /api/avatar`  
- Headers: `Content-Type: multipart/form-data`

</gsl-description>

<gsl-label>

## Outputs:
</gsl-label>
<gsl-description>

- Status: `201 Created` on success  
- Body: `{ "image_url": "<CDN path>" }`  
- Errors: `400` for invalid file, `413` for oversized image

</gsl-description>

<gsl-label>

## Constraints:
</gsl-label>
<gsl-description>

- Must reject unsupported file types  
- Must validate file size before upload  
- Must store using deterministic, traceable filename logic  
- Must support idempotent retry behavior on network failure

</gsl-description>
</gsl-block>

<gsl-template-guide>

## 📌 How This Template Works

This document is a template for writing `spec` prompts. It includes structural elements, section labels, and content guidance.  
When a user or agent populates this file with real project intent, the `<gsl-template-guide>` section must be removed.  
Only the `<gsl-header>` and `<gsl-block>` elements should remain in the final prompt.

</gsl-template-guide>
</gsl-template>
