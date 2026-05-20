import { useCallback, useEffect, useRef, useState } from "react";
import { FileText, Trash2, Upload } from "lucide-react";
import api from "../services/api";
import type { Document } from "../types";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const load = useCallback(async () => {
    const { data } = await api.get<Document[]>("/documents");
    setDocuments(data);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const upload = async (file: File) => {
    setError("");
    setUploading(true);
    const form = new FormData();
    form.append("file", file);
    try {
      await api.post("/documents/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await load();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data
        ?.detail;
      setError(typeof detail === "string" ? detail : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) upload(file);
    e.target.value = "";
  };

  const remove = async (id: number) => {
    await api.delete(`/documents/${id}`);
    setDocuments((prev) => prev.filter((d) => d.id !== id));
  };

  const statusColor = (status: string) => {
    if (status === "ready") return "text-emerald-400 bg-emerald-400/10";
    if (status === "failed") return "text-red-400 bg-red-400/10";
    return "text-amber-400 bg-amber-400/10";
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Knowledge Base</h1>
          <p className="text-slate-400 text-sm mt-1">
            Upload PDF or TXT files for embedding-based retrieval
          </p>
        </div>
        <button
          onClick={() => fileRef.current?.click()}
          className="btn-primary flex items-center gap-2"
          disabled={uploading}
        >
          <Upload className="w-4 h-4" />
          {uploading ? "Uploading..." : "Upload"}
        </button>
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.txt"
          className="hidden"
          onChange={onFileChange}
        />
      </div>

      {error && (
        <div className="mb-4 bg-red-500/10 border border-red-500/30 text-red-300 text-sm px-4 py-2 rounded-lg">
          {error}
        </div>
      )}

      <div className="card overflow-hidden">
        {documents.length === 0 ? (
          <div className="p-12 text-center text-slate-500">
            <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No documents yet. Upload your first file.</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 text-left">
                <th className="p-4 font-medium">Filename</th>
                <th className="p-4 font-medium">Type</th>
                <th className="p-4 font-medium">Chunks</th>
                <th className="p-4 font-medium">Status</th>
                <th className="p-4 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                  <td className="p-4 font-medium">{doc.filename}</td>
                  <td className="p-4 uppercase text-slate-400">{doc.file_type}</td>
                  <td className="p-4">{doc.chunk_count}</td>
                  <td className="p-4">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-medium ${statusColor(doc.status)}`}
                    >
                      {doc.status}
                    </span>
                  </td>
                  <td className="p-4 text-right">
                    <button
                      onClick={() => remove(doc.id)}
                      className="p-2 text-slate-500 hover:text-red-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
