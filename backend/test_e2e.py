import urllib.request
import json
import time
import os
import mimetypes

def make_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    
    req_data = None
    if data is not None:
        if isinstance(data, dict):
            req_data = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"
        else:
            req_data = data
            
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.read().decode('utf-8')}")
        raise

def encode_multipart_formdata(fields, files):
    boundary = b'----WebKitFormBoundary7MA4YWxkTrZu0gW'
    lines = []
    for name, value in fields.items():
        lines.append(b'--' + boundary)
        lines.append(f'Content-Disposition: form-data; name="{name}"'.encode('utf-8'))
        lines.append(b'')
        lines.append(str(value).encode('utf-8'))
    for name, filepath in files.items():
        lines.append(b'--' + boundary)
        filename = os.path.basename(filepath)
        mimetype = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
        lines.append(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"'.encode('utf-8'))
        lines.append(f'Content-Type: {mimetype}'.encode('utf-8'))
        lines.append(b'')
        with open(filepath, 'rb') as f:
            lines.append(f.read())
    lines.append(b'--' + boundary + b'--')
    lines.append(b'')
    body = b'\r\n'.join(lines)
    headers = {'Content-Type': f'multipart/form-data; boundary={boundary.decode("utf-8")}'}
    return body, headers

def test_e2e():
    base_url = "http://localhost:8000/api/v1"
    
    # 1. Create a new medical report record
    print("Creating new report record...")
    status, report = make_request(
        f"{base_url}/reports",
        method="POST",
        data={"title": "E2E Diagnosis Test Report"}
    )
    assert status == 201, f"Failed to create report: {status}"
    report_id = report["id"]
    print(f"Created report record ID: {report_id}")
    
    # 2. Find a sample PDF to upload
    sample_pdf_path = "uploads/2026/06/7fa7c931_Brain_MRI_Report.pdf"
    if not os.path.exists(sample_pdf_path):
        # Find another PDF if this path doesn't exist
        for root, dirs, files in os.walk("uploads"):
            for file in files:
                if file.endswith(".pdf"):
                    sample_pdf_path = os.path.join(root, file)
                    break
    
    print(f"Using sample PDF for upload: {sample_pdf_path}")
    
    # 3. Upload file
    body, headers = encode_multipart_formdata(
        fields={"report_id": report_id},
        files={"file": sample_pdf_path}
    )
    
    print("Uploading file to trigger processing...")
    status, upload_res = make_request(
        f"{base_url}/upload",
        method="POST",
        data=body,
        headers=headers
    )
    assert status == 201, f"Upload failed: {status}"
    print("File uploaded successfully. Polling status...")
    
    # 4. Poll status until completed or failed
    max_retries = 30
    delay = 1.0
    for i in range(max_retries):
        status, poll_report = make_request(f"{base_url}/reports/{report_id}")
        assert status == 200
        current_status = poll_report["status"]
        print(f"Attempt {i+1}: Current status = {current_status}")
        
        if current_status == "completed":
            print("Processing completed successfully!")
            print("AI Summary (English) length:", len(poll_report.get("ai_summary") or ""))
            print("AI Summary (Hindi) length:", len(poll_report.get("hindi_summary") or ""))
            print("Patient Explanation (English) length:", len(poll_report.get("patient_explanation") or ""))
            print("Patient Explanation (Hindi) length:", len(poll_report.get("hindi_explanation") or ""))
            
            # Assertions
            assert poll_report.get("ai_summary"), "AI Summary is empty"
            assert poll_report.get("hindi_summary"), "Hindi AI Summary is empty"
            assert poll_report.get("patient_explanation"), "English Patient Explanation is empty"
            assert poll_report.get("hindi_explanation"), "Hindi Patient Explanation is empty"
            assert "यह जानकारी केवल समझाने के उद्देश्य से है" not in poll_report.get("hindi_explanation"), "Disclaimer should not be in the raw database field, it belongs to the frontend rendering"
            
            print("E2E Test Passed Successfully!")
            break
        elif current_status == "failed":
            raise Exception("Processing failed in the backend pipeline.")
            
        time.sleep(delay)
    else:
        raise TimeoutError("Polling timed out.")

if __name__ == "__main__":
    test_e2e()
