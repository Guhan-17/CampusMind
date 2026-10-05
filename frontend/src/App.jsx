import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "https://campusmind-d9yi.onrender.com";
const suggestedQuestions = [
  "When should I pay my college fees?",
  "How can I pay my semester fees?",
  "What are the hostel rules?",
  "Can students use the college library?",
  "What should I carry to the examination?",
  "What information is available about placements?",
];

function App() {
  // ============================================================
  // APP MODE
  // ============================================================

  const [mode, setMode] = useState("student");

  // ============================================================
  // STUDENT CHAT
  // ============================================================

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  // ============================================================
  // ADMIN AUTH
  // ============================================================

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [token, setToken] = useState(
    localStorage.getItem("campusmind_token") || ""
  );

  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState("");

  // ============================================================
  // ADMIN DOCUMENTS
  // ============================================================

  const [selectedFile, setSelectedFile] = useState(null);

  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState("");

  const [documents, setDocuments] = useState([]);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [documentsError, setDocumentsError] = useState("");

  const [deleteLoading, setDeleteLoading] = useState("");

  // ============================================================
  // ASK QUESTION
  // ============================================================

  const askQuestion = async (text) => {
    const userQuestion = text.trim();

    if (!userQuestion || loading) return;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: userQuestion,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong.");
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            data.answer ||
            "Sorry, I could not generate an answer.",
        },
      ]);
    } catch (error) {
      console.error("CampusMind error:", error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't connect to CampusMind. Please make sure the backend is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    askQuestion(question);
  };

  // ============================================================
  // ADMIN LOGIN
  // ============================================================

  const handleLogin = async (e) => {
    e.preventDefault();

    setLoginError("");
    setLoginLoading(true);

    try {
      const formData = new URLSearchParams();

      formData.append("username", username);
      formData.append("password", password);

      const response = await fetch(`${API_URL}/admin/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Invalid username or password."
        );
      }

      if (!data.access_token) {
        throw new Error("No access token received.");
      }

      localStorage.setItem(
        "campusmind_token",
        data.access_token
      );

      setToken(data.access_token);

      setUsername("");
      setPassword("");
      setLoginError("");
    } catch (error) {
      console.error("Login error:", error);

      setLoginError(
        error.message || "Login failed. Please try again."
      );
    } finally {
      setLoginLoading(false);
    }
  };

  // ============================================================
  // ADMIN LOGOUT
  // ============================================================

  const handleLogout = () => {
    localStorage.removeItem("campusmind_token");

    setToken("");
    setSelectedFile(null);
    setUploadMessage("");
    setUploadError("");
    setDocuments([]);
    setDocumentsError("");
  };

  // ============================================================
  // LOAD DOCUMENTS
  // ============================================================

  const loadDocuments = async () => {
    if (!token) return;

    setDocumentsLoading(true);
    setDocumentsError("");

    try {
      const response = await fetch(
        `${API_URL}/admin/documents`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (response.status === 401) {
        handleLogout();
        throw new Error(
          "Your login session has expired. Please login again."
        );
      }

      if (!response.ok) {
        throw new Error(
          data.detail || "Could not load documents."
        );
      }

      setDocuments(data.documents || []);
    } catch (error) {
      console.error("Load documents error:", error);

      setDocumentsError(
        error.message || "Could not load documents."
      );
    } finally {
      setDocumentsLoading(false);
    }
  };

  // ============================================================
  // LOAD DOCUMENTS WHEN ADMIN DASHBOARD OPENS
  // ============================================================

  useEffect(() => {
    if (mode === "admin" && token) {
      loadDocuments();
    }
  }, [mode, token]);

  // ============================================================
  // FILE SELECTION
  // ============================================================

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];

    setUploadMessage("");
    setUploadError("");

    if (!file) {
      setSelectedFile(null);
      return;
    }

    const extension = file.name
      .toLowerCase()
      .slice(file.name.lastIndexOf("."));

    if (extension !== ".pdf" && extension !== ".txt") {
      setUploadError(
        "Only PDF and TXT files are allowed."
      );

      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  };

  // ============================================================
  // ADMIN UPLOAD
  // ============================================================

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError("Please select a file first.");
      return;
    }

    if (!token) {
      setUploadError(
        "You are not authenticated. Please login again."
      );
      return;
    }

    setUploadLoading(true);
    setUploadMessage("");
    setUploadError("");

    try {
      const formData = new FormData();

      formData.append("file", selectedFile);

      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();

      if (response.status === 401) {
        handleLogout();

        throw new Error(
          "Your login session has expired. Please login again."
        );
      }

      if (!response.ok) {
        throw new Error(
          data.detail || "Upload failed."
        );
      }

      setUploadMessage(
        `Successfully uploaded: ${data.filename}`
      );

      setSelectedFile(null);

      const fileInput =
        document.getElementById("document-file");

      if (fileInput) {
        fileInput.value = "";
      }

      // Reload document list
      await loadDocuments();
    } catch (error) {
      console.error("Upload error:", error);

      setUploadError(
        error.message || "Could not upload document."
      );
    } finally {
      setUploadLoading(false);
    }
  };

  // ============================================================
  // DELETE DOCUMENT
  // ============================================================

  const handleDelete = async (filename) => {
    if (!token) {
      setDocumentsError(
        "You are not authenticated. Please login again."
      );
      return;
    }

    const confirmed = window.confirm(
      `Are you sure you want to delete "${filename}"?\n\nThe knowledge base will also be rebuilt.`
    );

    if (!confirmed) return;

    setDeleteLoading(filename);
    setDocumentsError("");

    try {
      const response = await fetch(
        `${API_URL}/admin/documents/${encodeURIComponent(
          filename
        )}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (response.status === 401) {
        handleLogout();

        throw new Error(
          "Your login session has expired. Please login again."
        );
      }

      if (!response.ok) {
        throw new Error(
          data.detail || "Could not delete document."
        );
      }

      // Reload documents after deletion
      await loadDocuments();

      setUploadMessage(
        `Deleted ${filename} and updated the knowledge base.`
      );
    } catch (error) {
      console.error("Delete error:", error);

      setDocumentsError(
        error.message || "Could not delete document."
      );
    } finally {
      setDeleteLoading("");
    }
  };

  // ============================================================
  // FORMAT FILE SIZE
  // ============================================================

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";

    if (!bytes) return "Unknown size";

    const units = [
      "Bytes",
      "KB",
      "MB",
      "GB",
    ];

    const index = Math.floor(
      Math.log(bytes) / Math.log(1024)
    );

    return `${(
      bytes / Math.pow(1024, index)
    ).toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
  };

  // ============================================================
  // FORMAT DATE
  // ============================================================

  const formatDate = (dateString) => {
    if (!dateString) return "Unknown date";

    const date = new Date(dateString);

    if (Number.isNaN(date.getTime())) {
      return dateString;
    }

    return date.toLocaleString("en-IN", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  };

  // ============================================================
  // ADMIN LOGIN SCREEN
  // ============================================================

  const renderAdminLogin = () => {
    return (
      <main className="main admin-main">
        <section className="admin-login-card">

          <div className="admin-login-icon">
            🔐
          </div>

          <div className="admin-login-title">
            <span>CampusMind</span>
            <h2>Admin Login</h2>
          </div>

          <p className="admin-login-description">
            Sign in to manage college documents and
            maintain the CampusMind knowledge base.
          </p>

          <form
            onSubmit={handleLogin}
            className="admin-form"
          >
            <div className="form-group">
              <label>Username</label>

              <input
                type="text"
                placeholder="Enter admin username"
                value={username}
                onChange={(e) =>
                  setUsername(e.target.value)
                }
                disabled={loginLoading}
              />
            </div>

            <div className="form-group">
              <label>Password</label>

              <input
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={(e) =>
                  setPassword(e.target.value)
                }
                disabled={loginLoading}
              />
            </div>

            {loginError && (
              <div className="error-message">
                <span>⚠️</span>
                {loginError}
              </div>
            )}

            <button
              type="submit"
              className="primary-button login-button"
              disabled={
                loginLoading ||
                !username ||
                !password
              }
            >
              {loginLoading
                ? "Signing in..."
                : "Sign In"}
            </button>
          </form>

          <div className="secure-note">
            🔒 Admin access only
          </div>
        </section>
      </main>
    );
  };

  // ============================================================
  // ADMIN DASHBOARD
  // ============================================================

  const renderAdminDashboard = () => {
    return (
      <main className="main admin-main">

        <section className="admin-dashboard">

          {/* Dashboard Header */}
          <div className="dashboard-heading">

            <div>
              <div className="eyebrow">
                ADMIN PANEL
              </div>

              <h2>
                Document Management
              </h2>

              <p>
                Manage the documents used by
                CampusMind to answer student questions.
              </p>
            </div>

            <button
              className="refresh-button"
              onClick={loadDocuments}
              disabled={documentsLoading}
            >
              {documentsLoading
                ? "↻ Loading..."
                : "↻ Refresh"}
            </button>
          </div>

          {/* Upload Card */}
          <div className="upload-card">

            <div className="section-heading">
              <div className="section-icon">
                ⬆
              </div>

              <div>
                <h3>
                  Add College Document
                </h3>

                <p>
                  Upload PDF or TXT files containing
                  official college information.
                </p>
              </div>
            </div>

            <div className="upload-area">

              <label
                htmlFor="document-file"
                className="choose-file-button"
              >
                📁 Choose File
              </label>

              <input
                id="document-file"
                type="file"
                accept=".pdf,.txt"
                onChange={handleFileChange}
                disabled={uploadLoading}
                className="file-input"
              />

              {selectedFile ? (
                <div className="selected-file-card">
                  <div className="file-icon">
                    {selectedFile.name
                      .toLowerCase()
                      .endsWith(".pdf")
                      ? "📕"
                      : "📄"}
                  </div>

                  <div className="selected-file-info">
                    <strong>
                      {selectedFile.name}
                    </strong>

                    <span>
                      {formatFileSize(
                        selectedFile.size
                      )}
                    </span>
                  </div>
                </div>
              ) : (
                <div className="file-hint">
                  No file selected
                </div>
              )}

              <button
                className="primary-button upload-button"
                onClick={handleUpload}
                disabled={
                  uploadLoading ||
                  !selectedFile
                }
              >
                {uploadLoading
                  ? "Uploading & rebuilding..."
                  : "Upload Document"}
              </button>
            </div>

            {uploadError && (
              <div className="error-message">
                <span>⚠️</span>
                {uploadError}
              </div>
            )}

            {uploadMessage && (
              <div className="success-message">
                <span>✓</span>
                {uploadMessage}
              </div>
            )}

            <div className="upload-note">
              <span>⚡</span>
              After upload, CampusMind automatically
              processes the document and rebuilds its
              knowledge base.
            </div>
          </div>

          {/* Documents Card */}
          <div className="documents-card">

            <div className="documents-header">

              <div>
                <div className="documents-title-row">
                  <h3>
                    Uploaded Documents
                  </h3>

                  <span className="document-count">
                    {documents.length}
                  </span>
                </div>

                <p>
                  Documents currently available
                  to CampusMind.
                </p>
              </div>

              <button
                className="small-refresh-button"
                onClick={loadDocuments}
                disabled={documentsLoading}
              >
                ↻
              </button>
            </div>

            {documentsError && (
              <div className="error-message">
                <span>⚠️</span>
                {documentsError}
              </div>
            )}

            {documentsLoading ? (
              <div className="documents-loading">
                <div className="spinner"></div>

                <p>
                  Loading documents...
                </p>
              </div>
            ) : documents.length === 0 ? (
              <div className="empty-documents">
                <div className="empty-icon">
                  📂
                </div>

                <h4>
                  No uploaded documents
                </h4>

                <p>
                  Upload a PDF or TXT document
                  to add information to CampusMind.
                </p>
              </div>
            ) : (
              <div className="document-list">

                {documents.map((document) => (
                  <div
                    className="document-item"
                    key={document.filename}
                  >

                    <div className="document-icon">
                      {document.filename
                        .toLowerCase()
                        .endsWith(".pdf")
                        ? "📕"
                        : "📄"}
                    </div>

                    <div className="document-details">

                      <div className="document-name">
                        {document.filename}
                      </div>

                      <div className="document-meta">

                        <span>
                          {formatFileSize(
                            document.size
                          )}
                        </span>

                        <span className="meta-dot">
                          •
                        </span>

                        <span>
                          Uploaded{" "}
                          {formatDate(
                            document.uploaded_at
                          )}
                        </span>

                      </div>
                    </div>

                    <button
                      className="delete-button"
                      onClick={() =>
                        handleDelete(
                          document.filename
                        )
                      }
                      disabled={
                        deleteLoading ===
                        document.filename
                      }
                      title="Delete document"
                    >
                      {deleteLoading ===
                      document.filename
                        ? "..."
                        : "🗑️"}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Admin Information */}
          <div className="admin-security-card">

            <div className="security-icon">
              🔒
            </div>

            <div>
              <h4>
                Protected Admin Area
              </h4>

              <p>
                Only authenticated administrators
                can upload or delete college documents.
                Deleting a document automatically
                rebuilds the knowledge base.
              </p>
            </div>
          </div>

          <div className="dashboard-footer">
            <span>
              CampusMind Knowledge Management
            </span>

            <button
              className="logout-link"
              onClick={handleLogout}
            >
              Logout
            </button>
          </div>

        </section>
      </main>
    );
  };

  // ============================================================
  // STUDENT CHAT
  // ============================================================

  const renderStudentChat = () => {
    return (
      <main className="main">

        {messages.length === 0 ? (
          <section className="welcome">

            <div className="welcome-badge">
              <span>✦</span>
              AI COLLEGE ASSISTANT
            </div>

            <div className="welcome-icon">
              🎓
            </div>

            <h2>
              How can I help you today?
            </h2>

            <p>
              Ask CampusMind about college fees,
              exams, library, hostel, placements,
              and other college information.
            </p>

            <div className="suggestions">

              {suggestedQuestions.map(
                (item, index) => (
                  <button
                    key={index}
                    className="suggestion-card"
                    onClick={() =>
                      askQuestion(item)
                    }
                    disabled={loading}
                  >
                    <span className="suggestion-icon">
                      {index === 0 && "💰"}
                      {index === 1 && "💳"}
                      {index === 2 && "🏠"}
                      {index === 3 && "📚"}
                      {index === 4 && "📝"}
                      {index === 5 && "💼"}
                    </span>

                    <span className="suggestion-text">
                      {item}
                    </span>

                    <span className="suggestion-arrow">
                      →
                    </span>
                  </button>
                )
              )}

            </div>
          </section>
        ) : (
          <section className="chat">

            {messages.map(
              (message, index) => (
                <div
                  key={index}
                  className={`message ${
                    message.role === "user"
                      ? "user-message"
                      : "bot-message"
                  }`}
                >
                  <div className="message-label">
                    {message.role === "user"
                      ? "You"
                      : "CampusMind"}
                  </div>

                  <div className="message-content">
                    {message.content}
                  </div>
                </div>
              )
            )}

            {loading && (
              <div className="message bot-message">
                <div className="message-label">
                  CampusMind
                </div>

                <div className="typing">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </section>
        )}
      </main>
    );
  };

  // ============================================================
  // MAIN UI
  // ============================================================

  return (
    <div className="app">

      <header className="header">

        <div className="logo">

          <div className="logo-icon">
            C
          </div>

          <div>
            <h1>
              CampusMind
            </h1>

            <p>
              College Information Assistant
            </p>
          </div>
        </div>

        <div className="header-actions">

          {mode === "student" && (
            <button
              className="mode-button"
              onClick={() =>
                setMode("admin")
              }
            >
              🔐 Admin
            </button>
          )}

          {mode === "admin" && (
            <button
              className="mode-button"
              onClick={() =>
                setMode("student")
              }
            >
              🎓 Student
            </button>
          )}

          <div className="status">
            <span className="status-dot"></span>
            Online
          </div>

        </div>
      </header>

      {mode === "student" &&
        renderStudentChat()}

      {mode === "admin" &&
        (!token
          ? renderAdminLogin()
          : renderAdminDashboard())}

      {mode === "student" && (
        <div className="input-area">

          <form
            onSubmit={handleSubmit}
            className="input-form"
          >
            <input
              type="text"
              value={question}
              onChange={(e) =>
                setQuestion(e.target.value)
              }
              placeholder="Ask CampusMind something..."
              disabled={loading}
            />

            <button
              type="submit"
              disabled={
                loading ||
                !question.trim()
              }
            >
              {loading ? "..." : "➤"}
            </button>
          </form>

          <p className="footer-text">
            CampusMind answers using information
            from the college knowledge base.
          </p>

        </div>
      )}
    </div>
  );
}

export default App;