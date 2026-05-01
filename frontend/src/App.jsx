// frontend/src/App.jsx

import React, { useState, useEffect } from "react";
import api from "./api";

const cleanText = (text) => {
  if (!text) return "";

  return text
    .replace(/\*\*/g, "")
    .replace(/###/g, "")
    .replace(/##/g, "")
    .replace(/#/g, "")
    .trim();
};

const cleanIntroLines = (text) => {
  if (!text) return "";
  return text
    .split("\n")
    .map(line => line.trim())
    .filter(line => {
      const lower = line.toLowerCase();
      if (lower.startsWith("here are")) return false;
      if (lower.startsWith("sure")) return false;
      if (lower.startsWith("certainly")) return false;
      return true;
    })
    .filter(line => line.length > 0)
    .join("\n");
};

export default function App() {
  const [file, setFile] = useState(null);
  const [slides, setSlides] = useState([]);
  const [loading, setLoading] = useState(false);
  const [reports, setReports] = useState([]);

  const loadReports = async () => {
    try {
      const res = await api.get("/reports");
      setReports(res.data.reports || []);
    } catch (error) {
      console.log(error);
    }
  };

  useEffect(() => {
    loadReports();
  }, []);

  const upload = async () => {
    if (!file) {
      alert("Please upload a PDF first.");
      return;
    }

    try {
      setLoading(true);

      const form = new FormData();
      form.append("file", file);

      const res = await api.post("/upload-pdf", form);

      setSlides(res.data.slides || []);
      loadReports();
    } catch (error) {
      console.log(error);
      alert("Backend/API Error");
    } finally {
      setLoading(false);
    }
  };

  const overallScore =
    slides.length > 0
      ? Math.round(
        slides.reduce((sum, item) => sum + item.score, 0) /
        slides.length
      )
      : 0;

  const getColor = (score) => {
    if (score >= 80) return "#16a34a";
    if (score >= 60) return "#f59e0b";
    return "#dc2626";
  };

  const parseAgents = (text) => {
    if (!text) return {};

    const sections = {
      Investor: "",
      Market: "",
      Product: "",
      Risk: "",
      Finance: ""
    };

    const keys = Object.keys(sections);
    let currentKey = null;

    const lines = text.split('\n');
    for (const line of lines) {
      const trimmed = line.trim();
      if (keys.some(k => trimmed === `${k}:`)) {
        currentKey = keys.find(k => trimmed === `${k}:`);
      } else if (currentKey) {
        sections[currentKey] += line + '\n';
      }
    }

    return sections;
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(135deg,#eef2ff,#f5f3ff,#ffffff)",
        padding: "40px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <div
        style={{
          maxWidth: "1400px",
          width: "100%",
          margin: "auto",
        }}
      >
        {/* Header */}
        <h1
          style={{
            fontSize: "52px",
            marginBottom: "10px",
            color: "#4f46e5",
            fontWeight: "bold",
          }}
        >
          Pitch Deck AI Analyzer
        </h1>

        <p
          style={{
            color: "#555",
            fontSize: "20px",
            marginBottom: "35px",
          }}
        >
          Upload your startup pitch deck and get
          investor-grade feedback instantly.
        </p>

        {/* Upload Card */}
        <div
          style={{
            background: "#ffffff",
            padding: "35px",
            borderRadius: "24px",
            boxShadow: "0 12px 35px rgba(0,0,0,0.08)",
            marginBottom: "35px",
          }}
        >
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
            style={{
              marginBottom: "18px",
              fontSize: "16px",
            }}
          />

          <br />

          <button
            onClick={upload}
            style={{
              background: "#4f46e5",
              color: "white",
              border: "none",
              padding: "14px 30px",
              borderRadius: "12px",
              fontSize: "17px",
              cursor: "pointer",
              fontWeight: "bold",
              marginRight: "12px",
            }}
          >
            Analyze Pitch Deck
          </button>

          <a
            href="http://127.0.0.1:8000/download-report"
            target="_blank"
            rel="noreferrer"
          >
            <button
              style={{
                background: "#16a34a",
                color: "white",
                border: "none",
                padding: "14px 30px",
                borderRadius: "12px",
                fontSize: "17px",
                cursor: "pointer",
                fontWeight: "bold",
              }}
            >
              Download Report
            </button>
          </a>

          {loading && (
            <p
              style={{
                marginTop: "18px",
                color: "#555",
                fontSize: "16px",
              }}
            >
              Running AI analysis...
            </p>
          )}
        </div>



        {/* Overall Score */}
        {slides.length > 0 && (
          <div
            style={{
              background: "#ffffff",
              padding: "30px",
              borderRadius: "24px",
              boxShadow: "0 12px 35px rgba(0,0,0,0.08)",
              marginBottom: "35px",
            }}
          >
            <h2
              style={{
                marginBottom: "12px",
                fontSize: "24px",
              }}
            >
              Overall Deck Score
            </h2>

            <div
              style={{
                fontSize: "64px",
                fontWeight: "bold",
                color: getColor(overallScore),
              }}
            >
              {overallScore}/100
            </div>
          </div>
        )}

        {/* Slide Cards */}
        {slides.map((s) => (
          <div
            key={s.slide_no}
            style={{
              background: "#ffffff",
              padding: "30px",
              borderRadius: "24px",
              boxShadow: "0 12px 35px rgba(0,0,0,0.08)",
              marginBottom: "32px",
            }}
          >
            {/* Top Header */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "25px",
              }}
            >
              <h2
                style={{
                  fontSize: "36px",
                  margin: 0,
                }}
              >
                Slide {s.slide_no}
              </h2>

              <span
                style={{
                  background: getColor(s.score),
                  color: "white",
                  padding: "10px 18px",
                  borderRadius: "14px",
                  fontWeight: "bold",
                  fontSize: "18px",
                }}
              >
                {s.score}/100
              </span>
            </div>

            {/* Extracted Content */}
            <div
              style={{
                background: "#eef2ff",
                padding: "22px",
                borderRadius: "18px",
                marginBottom: "22px",
              }}
            >
              <h3
                style={{
                  color: "#4338ca",
                  marginTop: 0,
                  marginBottom: "14px",
                  fontSize: "24px",
                }}
              >
                Extracted Content
              </h3>

              <p
                style={{
                  color: "#374151",
                  lineHeight: "1.9",
                  fontSize: "17px",
                  margin: 0,
                }}
              >
                {s.text}
              </p>
            </div>

            {/* Multi-Agent Feedback */}
            <div
              style={{
                marginBottom: "22px"
              }}
            >
              <h3
                style={{
                  marginBottom: "16px",
                  fontSize: "24px"
                }}
              >
                Multi-Agent Analysis
              </h3>

              {(() => {
                const agents = parseAgents(cleanText(s.feedback));

                const agentData = [
                  { title: "Investor", key: "Investor", content: agents.Investor?.trim(), color: "#22c55e" },
                  { title: "Market", key: "Market", content: agents.Market?.trim(), color: "#3b82f6" },
                  { title: "Product", key: "Product", content: agents.Product?.trim(), color: "#a855f7" },
                  { title: "Risk", key: "Risk", content: agents.Risk?.trim(), color: "#ef4444" },
                  { title: "Finance", key: "Finance", content: agents.Finance?.trim(), color: "#f59e0b" },
                ];

                const validAgents = agentData.filter(a => {
                  if (!a.content) return false;
                  const lower = a.content.toLowerCase();
                  if (lower.includes("no data") || lower.includes("no strong signals") || lower.includes("cannot infer")) return false;
                  return true;
                });

                if (validAgents.length === 0) {
                  return <p style={{ color: "#6b7280", fontStyle: "italic" }}>No valid insights extracted for this slide.</p>;
                }

                return (
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit, minmax(350px, 1fr))",
                      gap: "20px",
                      alignItems: "stretch",
                      width: "100%"
                    }}
                  >
                    {validAgents.map(a => (
                      <AgentCard key={a.key} title={a.title} content={a.content} color={a.color} />
                    ))}
                  </div>
                );
              })()}
            </div>


            {/* Rewrite */}
            <div
              style={{
                background: "#fff7ed",
                padding: "24px",
                borderRadius: "18px",
                borderLeft: "6px solid #f97316",
              }}
            >
              <h3
                style={{
                  color: "#ea580c",
                  marginTop: 0,
                  marginBottom: "14px",
                  fontSize: "24px",
                }}
              >
                Stronger Rewrite
              </h3>

              <p
                style={{
                  color: "#1f2937",
                  lineHeight: "2",
                  fontSize: "17px",
                  whiteSpace: "pre-line",
                  margin: 0,
                }}
              >
                {cleanText(s.rewrite)}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}



function AgentCard({ title, content, color }) {
  const cleanedContent = cleanIntroLines(content);
  // Extract bullet points
  const bullets = cleanedContent.split("\n").filter(l => l.trim().length > 0);

  return (
    <div
      style={{
        background: "#ffffff",
        padding: "24px",
        borderRadius: "16px",
        borderTop: `6px solid ${color}`,
        boxShadow: "0 10px 25px rgba(0,0,0,0.05)",
        display: "flex",
        flexDirection: "column",
        wordBreak: "break-word",
      }}
    >
      <h4
        style={{
          marginTop: 0,
          marginBottom: "16px",
          color: "#1f2937",
          fontSize: "20px",
          fontWeight: "bold",
        }}
      >
        {title}
      </h4>

      <ul
        style={{
          margin: 0,
          paddingLeft: "18px",
          color: "#4b5563",
          fontSize: "14px",
          lineHeight: "1.6",

          wordBreak: "break-word",   // FIX 5
        }}
      >
        {bullets.map((b, i) => {
          let text = b.replace(/^[-*•]\s*/, "").trim();

          // Truncate to max 2 sentences just in case
          const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
          if (sentences.length > 2) {
            text = sentences.slice(0, 2).join(" ").trim();
          }

          return (
            <li key={i} style={{ marginBottom: "10px" }}>
              {text}
            </li>
          );
        })}
      </ul>
    </div>
  );
}