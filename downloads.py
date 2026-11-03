"""Bounded, resumable file transfer. No redirects or user-controlled file paths."""
import re
from django.http import FileResponse, HttpResponse, StreamingHttpResponse

class Slice:
    def __init__(self, file, remaining): self.file, self.remaining = file, remaining
    def __iter__(self): return self
    def __next__(self):
        if self.remaining <= 0: raise StopIteration
        chunk = self.file.read(min(65536, self.remaining))
        if not chunk: raise StopIteration
        self.remaining -= len(chunk)
        return chunk
    def close(self): self.file.close()

def send_apk(request, file):
    import os
    stat = os.fstat(file.fileno()); size = stat.st_size
    etag = '"%x-%x"' % (size, stat.st_mtime_ns)
    start, end, status = 0, size - 1, 200
    value = request.headers.get('Range', '')
    if request.method == 'GET' and value and request.headers.get('If-Range', etag) == etag:
        match = re.fullmatch(r'bytes=(\d{0,20})-(\d{0,20})', value)
        valid = bool(match and any(match.groups()))
        if valid:
            a,b = match.groups()
            if a:
                start = int(a); end = min(int(b), size-1) if b else size-1
                valid = start < size and start <= end
            else:
                suffix = int(b); valid = suffix > 0
                start = max(0, size-suffix)
        if not valid:
            file.close(); response = HttpResponse(status=416)
            response['Content-Range'] = f'bytes */{size}'
            response['Accept-Ranges'] = 'bytes'
            return response
        status = 206
    if request.method == 'HEAD':
        file.close(); response = HttpResponse(content_type='application/vnd.android.package-archive')
    elif status == 206:
        file.seek(start)
        response = StreamingHttpResponse(Slice(file,end-start+1),status=206,content_type='application/vnd.android.package-archive')
        response['Content-Range'] = f'bytes {start}-{end}/{size}'
    else:
        response = FileResponse(file,content_type='application/vnd.android.package-archive')
    response['Content-Length'] = str(end-start+1)
    response['Content-Disposition'] = 'attachment; filename="e-dukon.apk"'
    response['Accept-Ranges'] = 'bytes'
    response['ETag'] = etag
    response['Cache-Control'] = 'private, no-transform'
    response['X-Content-Type-Options'] = 'nosniff'
    return response
