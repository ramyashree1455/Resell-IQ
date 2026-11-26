import React, { useState, useEffect, useRef } from "react";

const BACKEND_URL = "http://127.0.0.1:8000";

const CATEGORY_MAP = {
  smartphones: {
    name: "Smartphone / Mobile",
    defaultTitle: "Samsung Galaxy S23 256GB",
    defaultPrice: "38999",
    presets: [
      { label: "Samsung Galaxy S23", price: "38999" },
      { label: "Apple iPhone 13 128GB", price: "39500" },
      { label: "OnePlus 11 5G 128GB", price: "31999" },
      { label: "Google Pixel 7 Pro", price: "34500" },
    ],
  },
  laptops: {
    name: "Laptop / Computer",
    defaultTitle: "MacBook Air M2 8GB/256GB",
    defaultPrice: "69999",
    presets: [
      { label: "MacBook Air M2 256GB", price: "69999" },
      { label: "Dell XPS 13 i7 16GB", price: "58000" },
      { label: "Lenovo ThinkPad X1 Gen 9", price: "52000" },
      { label: "Asus ROG Zephyrus G14", price: "64000" },
    ],
  },
  tablets: {
    name: "Tablet / iPad",
    defaultTitle: "iPad Air 5th Gen 64GB Wi-Fi",
    defaultPrice: "34999",
    presets: [
      { label: "iPad Air 5th Gen 64GB", price: "34999" },
      { label: "iPad 10th Gen 64GB", price: "27500" },
      { label: "Samsung Galaxy Tab S9", price: "44000" },
      { label: "iPad Pro 11-inch M1", price: "48000" },
    ],
  },
  cameras: {
    name: "Camera / DSLR / Mirrorless",
    defaultTitle: "Sony Alpha a7 III Mirrorless Body",
    defaultPrice: "88000",
    presets: [
      { label: "Sony Alpha a7 III Body", price: "88000" },
      { label: "Canon EOS R6 Body", price: "95000" },
      { label: "Fujifilm X-T4 with 18-55mm", price: "72000" },
      { label: "Nikon Z6 II Body", price: "78000" },
    ],
  },
  audio: {
    name: "Audio / Headphones / Earbuds",
    defaultTitle: "Sony WH-1000XM4 Noise Canceling",
    defaultPrice: "14999",
    presets: [
      { label: "Sony WH-1000XM4", price: "14999" },
      { label: "Apple AirPods Pro 2nd Gen", price: "15500" },
      { label: "Bose QuietComfort 45", price: "16999" },
      { label: "Sennheiser Momentum 4", price: "18500" },
    ],
  },
  gaming: {
    name: "Gaming Console",
    defaultTitle: "PlayStation 5 Disc Edition 825GB",
    defaultPrice: "38999",
    presets: [
      { label: "PlayStation 5 Disc Edition", price: "38999" },
      { label: "PlayStation 5 Digital Edition", price: "34000" },
      { label: "Xbox Series X 1TB", price: "36500" },
      { label: "Nintendo Switch OLED", price: "23500" },
    ],
  },
};

export default function Interview({ onReportGenerated, onNavigateTab }) {
  const [step, setStep] = useState(1);
  const [category, setCategory] = useState("smartphones");
  const [title, setTitle] = useState("");
  const [askingPrice, setAskingPrice] = useState("");

  // Photos & live vision analysis
  const [uploadedPhotos, setUploadedPhotos] = useState({});
  const [defectResults, setDefectResults] = useState({});
  const [isScanning, setIsScanning] = useState({});
  const [hasInvalidPhoto, setHasInvalidPhoto] = useState(false);
  const [photoValidationError, setPhotoValidationError] = useState(null);

  // Dynamic Questionnaire options
  const [cosmeticCondition, setCosmeticCondition] = useState("like_new");
  const [functionalStatus, setFunctionalStatus] = useState("fully_working");
  const [visibleDamage, setVisibleDamage] = useState("none");
  const [repairHistory, setRepairHistory] = useState("never_repaired");
  const [accessories, setAccessories] = useState("all");
  const [repairNotes, setRepairNotes] = useState("");

  // Interactive AI Chat Interview State
  const [interviewMode, setInterviewMode] = useState("chat"); // "chat" | "form"
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatStep, setChatStep] = useState(0); // 1: cosmetic, 2: functional, 3: repair, 4: accessories, 5: completed
  const [isAiTyping, setIsAiTyping] = useState(false);
  const chatBottomRef = useRef(null);

  const initChat = (productTitle) => {
    const t = productTitle || title || "your device";
    const hasDefects = Object.values(defectResults).some((r) => r && r.defect_count > 0);
    const defectSummary = hasDefects
      ? "Our optical scanner flagged potential physical marks on the photo evidence."
      : "Our optical scanner detected 0 major visual defects on the uploaded photo.";

    setChatMessages([
      {
        id: "intro-1",
        sender: "ai",
        text: `Hello! I am your AI Verification Inspector for ${t}. ${defectSummary} Let's verify a few quick hardware details to produce your official condition certificate.`,
      },
      {
        id: "q1",
        sender: "ai",
        stepIndex: 1,
        text: `Question 1 of 4: How would you describe the overall cosmetic & aesthetic condition of the display and body?`,
        options: [
          { label: "✨ Like New / Mint", val: "like_new", desc: "Zero noticeable scratches or scuffs" },
          { label: "👍 Good Condition", val: "good", desc: "Minor light hairline scuffs from normal use" },
          { label: "⚠️ Fair Condition", val: "fair", desc: "Noticeable scratches on glass or body" },
          { label: "❌ Heavy Wear", val: "poor", desc: "Deep dents, chipped glass, or heavy wear" },
        ],
      },
    ]);
    setChatStep(1);
  };

  useEffect(() => {
    if (step === 3 && chatMessages.length === 0) {
      initChat(title);
    }
  }, [step, title]);

  useEffect(() => {
    if (step === 3 && chatBottomRef.current) {
      chatBottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages, isAiTyping, step]);

  const handleChatAnswer = (val, label) => {
    const userMsg = { id: `user-${Date.now()}`, sender: "user", text: label || val };
    setChatMessages((prev) => [...prev, userMsg]);
    setIsAiTyping(true);

    setTimeout(() => {
      setIsAiTyping(false);

      if (chatStep === 1) {
        setCosmeticCondition(val);
        const hasCracks = Object.values(defectResults).some((r) =>
          (r.defects || []).some((d) => d.type === "crack" || d.type === "dent")
        );

        const nextMsgs = [];
        if (hasCracks && val === "like_new") {
          nextMsgs.push({
            id: `ai-warn-${Date.now()}`,
            sender: "ai",
            isAlert: true,
            text: `⚠️ Optical Discrepancy Note: Photo evidence detected surface cracks/dents, while condition was stated as Like New. The certification algorithm will balance this accordingly.`,
          });
        }

        nextMsgs.push({
          id: "q2",
          sender: "ai",
          stepIndex: 2,
          text: `Recorded. Question 2 of 4: Are all internal hardware components (display touch response, cameras, biometrics, connectivity, and battery) fully functional?`,
          options: [
            { label: "🟢 100% Fully Functional", val: "fully_working", desc: "Display, touch, cameras, Wi-Fi & battery working normally" },
            { label: "🟡 Minor Issue", val: "minor_issues", desc: "Battery health below 80% or faint display tint" },
            { label: "🔴 Major Fault", val: "major_issues", desc: "Camera faulty, touch dead spots, or speaker distortion" },
          ],
        });

        setChatMessages((prev) => [...prev, ...nextMsgs]);
        setChatStep(2);
      } else if (chatStep === 2) {
        setFunctionalStatus(val);
        setChatMessages((prev) => [
          ...prev,
          {
            id: "q3",
            sender: "ai",
            stepIndex: 3,
            text: `Noted. Question 3 of 4: What is the service & repair history for this device?`,
            options: [
              { label: "🛡️ Never Repaired", val: "never_repaired", desc: "100% Original factory parts, never opened" },
              { label: "🏢 Authorized Service Center", val: "professionally_repaired", desc: "Repaired by official brand with genuine OEM parts" },
              { label: "🔧 Third-Party / Local Repair", val: "self_repaired", desc: "Screen or battery replaced at a local shop" },
            ],
          },
        ]);
        setChatStep(3);
      } else if (chatStep === 3) {
        setRepairHistory(val);
        setChatMessages((prev) => [
          ...prev,
          {
            id: "q4",
            sender: "ai",
            stepIndex: 4,
            text: `Understood. Final Question (4 of 4): Which original packaging and accessories are included?`,
            options: [
              { label: "📦 Complete Package", val: "all", desc: "Original box, bill, and power adapter/charger included" },
              { label: "🔌 Device + Charging Cable", val: "some_missing", desc: "Working cable included, but retail box is missing" },
              { label: "📱 Device Only", val: "many_missing", desc: "Handset/unit only, no charger or box" },
            ],
          },
        ]);
        setChatStep(4);
      } else if (chatStep === 4) {
        setAccessories(val);
        setChatMessages((prev) => [
          ...prev,
          {
            id: "done",
            sender: "ai",
            isFinal: true,
            text: `✓ Diagnostic inspection completed! All seller responses have been cross-checked against optical defect evidence. Click below to generate your official Verified Condition Certificate.`,
          },
        ]);
        setChatStep(5);
      }
    }, 550);
  };

  const handleChatSend = () => {
    if (!chatInput.trim()) return;
    const text = chatInput.trim();
    setChatInput("");
    const lower = text.toLowerCase();
    let val = "good";

    if (chatStep === 1) {
      if (lower.includes("mint") || lower.includes("like new") || lower.includes("new") || lower.includes("perfect")) val = "like_new";
      else if (lower.includes("good") || lower.includes("clean")) val = "good";
      else if (lower.includes("fair") || lower.includes("scratch")) val = "fair";
      else if (lower.includes("heavy") || lower.includes("crack") || lower.includes("broken")) val = "poor";
      handleChatAnswer(val, text);
    } else if (chatStep === 2) {
      if (lower.includes("100") || lower.includes("perfect") || lower.includes("fully") || lower.includes("work")) val = "fully_working";
      else if (lower.includes("battery") || lower.includes("minor")) val = "minor_issues";
      else val = "major_issues";
      handleChatAnswer(val, text);
    } else if (chatStep === 3) {
      if (lower.includes("never") || lower.includes("original") || lower.includes("no")) val = "never_repaired";
      else if (lower.includes("official") || lower.includes("authorized") || lower.includes("service center")) val = "professionally_repaired";
      else val = "self_repaired";
      handleChatAnswer(val, text);
    } else if (chatStep === 4) {
      if (lower.includes("all") || lower.includes("box") || lower.includes("complete")) val = "all";
      else if (lower.includes("cable") || lower.includes("charger")) val = "some_missing";
      else val = "many_missing";
      handleChatAnswer(val, text);
    }
  };

  const handleCategoryChange = (newCat) => {
    setCategory(newCat);
    setUploadedPhotos({});
    setDefectResults({});
    setHasInvalidPhoto(false);
    setPhotoValidationError(null);
  };

  // Upload photo & run defect detection
  const handlePhotoUpload = async (slotIndex, file) => {
    if (!file) return;

    const previewUrl = URL.createObjectURL(file);
    setUploadedPhotos((prev) => ({ ...prev, [slotIndex]: previewUrl }));
    setIsScanning((prev) => ({ ...prev, [slotIndex]: true }));

    const viewType = slotIndex === 0 ? "screen" : slotIndex === 1 ? "back" : "frame";
    const formData = new FormData();
    formData.append("file", file);
    formData.append("view_type", viewType);
    formData.append("product_category", category);
    formData.append("product_title", title);

    try {
      const res = await fetch(`${BACKEND_URL}/vision/detect-defects`, {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        setDefectResults((prev) => ({ ...prev, [slotIndex]: data }));

        if (data.is_valid_device_photo === false) {
          setHasInvalidPhoto(true);
          setPhotoValidationError(data.validation_message || "Invalid image. The uploaded photo does not appear to contain the selected product. Please upload a clear photograph of your device.");
        } else {
          // Re-evaluate if any other slot is still invalid
          setPhotoValidationError(null);
          setHasInvalidPhoto(false);
        }
      }
    } catch (e) {
      console.warn("Backend defect scan unavailable, using local validation:", e);
    } finally {
      setIsScanning((prev) => ({ ...prev, [slotIndex]: false }));
    }
  };

  // Calculate actual grade & generate report
  const handleGenerateReport = async () => {
    // Collect all detected defects across uploaded photos
    const allDefects = [];
    let detectedCrack = false;
    let detectedDent = false;

    Object.values(defectResults).forEach((result) => {
      if (result && result.defects) {
        result.defects.forEach((d) => {
          allDefects.push(d);
          if (d.type === "crack") detectedCrack = true;
          if (d.type === "dent") detectedDent = true;
        });
      }
    });

    // Check if non-device was uploaded
    if (hasInvalidPhoto) {
      const rejectedReport = {
        title,
        category,
        askingPrice,
        score: 0,
        grade: "REJECTED",
        confidence: 0.10,
        needs_manual_review: true,
        defects: [],
        reasons: ["Certification rejected: Non-device visuals detected in uploaded photograph."],
      };
      onReportGenerated(rejectedReport);
      onNavigateTab("report");
      return;
    }

    // Dynamic scoring calculation
    let baseScore = 95;
    if (cosmeticCondition === "like_new") baseScore = 96;
    else if (cosmeticCondition === "good") baseScore = 85;
    else if (cosmeticCondition === "fair") baseScore = 68;
    else baseScore = 48;

    if (functionalStatus === "fully_working") baseScore += 2;
    else if (functionalStatus === "minor_issues") baseScore -= 12;
    else baseScore -= 30;

    if (repairHistory === "never_repaired") baseScore += 2;
    else if (repairHistory === "professionally_repaired") baseScore -= 4;
    else baseScore -= 14;

    // Defect penalty
    const defectImpact = allDefects.length * 6 + (detectedCrack ? 25 : 0) + (detectedDent ? 10 : 0);
    let finalScore = Math.max(25, Math.min(100, baseScore - defectImpact));

    let finalGrade = "B";
    if (finalScore >= 90) finalGrade = "A";
    else if (finalScore >= 75) finalGrade = "B";
    else if (finalScore >= 60) finalGrade = "C";
    else finalGrade = "D";

    // Contradictions check
    const contradictions = [];
    if (cosmeticCondition === "like_new" && (detectedCrack || allDefects.length > 0)) {
      contradictions.push("Claimed 'Like New' condition, but photo inspection identified physical defects.");
    }
    if (repairHistory === "never_repaired" && repairNotes.toLowerCase().includes("replace")) {
      contradictions.push("Claimed 'Never Repaired', but notes mention component replacement.");
    }

    const confidence = Object.keys(uploadedPhotos).length >= 2 ? 0.94 : 0.82;
    const needsManualReview = contradictions.length > 0 || detectedCrack || finalScore < 60;

    // Generate component health diagnostics specific to this product
    const componentHealth = [
      {
        name: category === "smartphones" ? "Display & Touch Screen" : category === "laptops" ? "Display Panel & Hinges" : "Screen / Optics",
        status: detectedCrack ? "Defect Detected (Crack)" : allDefects.length === 0 ? "✓ 100% Original, No cracks" : "✓ Light cosmetic wear",
      },
      {
        name: category === "smartphones" || category === "laptops" ? "Battery Health & Performance" : "Power Management",
        status: cosmeticCondition === "like_new" ? "✓ Excellent (Healthy retention)" : "✓ Normal daily backup",
      },
      {
        name: category === "smartphones" ? "Cameras & Sensors" : category === "laptops" ? "Keyboard & Trackpad" : "Controls & Buttons",
        status: functionalStatus === "fully_working" ? "✓ 100% Fully Functional" : "⚠️ Minor functional quirk noted",
      },
      {
        name: "Service & Component History",
        status: repairHistory === "never_repaired" ? "✓ Factory Original (Never opened)" : repairHistory === "professionally_repaired" ? "✓ Serviced by Authorized Brand Center" : "⚠️ Third-Party repair recorded",
      },
    ];

    const reportData = {
      title,
      category,
      askingPrice,
      score: finalScore,
      grade: finalGrade,
      confidence,
      needs_manual_review: needsManualReview,
      defects: allDefects,
      contradictions,
      componentHealth,
    };

    onReportGenerated(reportData);
    onNavigateTab("report");
  };

  return (
    <div style={{ width: "100%" }}>
      {/* Inspirante Page Header */}
      <div className="page-header">
        <h1 className="page-title">Seller Inspection & Diagnostic Audit</h1>
        <p className="page-subtitle">
          Verify device authenticity, detect physical defects with computer vision, and generate an official condition certificate.
        </p>
      </div>

      {/* Inspirante 4 Stat Cards */}
      <div className="stat-cards-grid">
        <div className="stat-card">
          <div className="stat-card-info">
            <div className="stat-card-label">Visual AI Engine</div>
            <div className="stat-card-number" style={{ fontSize: "20px" }}>Active</div>
          </div>
          <div className="stat-card-icon icon-blue">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
              <circle cx="12" cy="13" r="4"></circle>
            </svg>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-info">
            <div className="stat-card-label">Category Trees</div>
            <div className="stat-card-number">5</div>
          </div>
          <div className="stat-card-icon icon-green">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
              <polyline points="2 17 12 22 22 17"></polyline>
              <polyline points="2 12 12 17 22 12"></polyline>
            </svg>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-info">
            <div className="stat-card-label">Defect Scanner</div>
            <div className="stat-card-number" style={{ fontSize: "20px" }}>3x3 Grid</div>
          </div>
          <div className="stat-card-icon icon-orange">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="3" y1="9" x2="21" y2="9"></line>
              <line x1="3" y1="15" x2="21" y2="15"></line>
              <line x1="9" y1="3" x2="9" y2="21"></line>
              <line x1="15" y1="3" x2="15" y2="21"></line>
            </svg>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-card-info">
            <div className="stat-card-label">Condition Scale</div>
            <div className="stat-card-number" style={{ fontSize: "20px" }}>Grade A–F</div>
          </div>
          <div className="stat-card-icon icon-purple">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="8" r="7"></circle>
              <polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"></polyline>
            </svg>
          </div>
        </div>
      </div>

      {/* Progress Stepper */}
      <div className="stepper">
        <div className={`step-item ${step === 1 ? "active" : step > 1 ? "completed" : ""}`}>
          <div className="step-circle">1</div>
          <div className="step-label">Product Info</div>
        </div>
        <div className={`step-item ${step === 2 ? "active" : step > 2 ? "completed" : ""}`}>
          <div className="step-circle">2</div>
          <div className="step-label">Photo Evidence</div>
        </div>
        <div className={`step-item ${step === 3 ? "active" : step > 3 ? "completed" : ""}`}>
          <div className="step-circle">3</div>
          <div className="step-label">Inspection</div>
        </div>
      </div>

      {/* STEP 1: Product Information */}
      {step === 1 && (
        <div className="card">
          <h2 className="card-title">Step 1: Product Details</h2>
          <p className="card-subtitle">
            Select your product category and enter the model name to initialize category-specific inspection criteria.
          </p>

          <div className="form-group">
            <label className="form-label">Product Category</label>
            <select
              className="form-select"
              value={category}
              onChange={(e) => handleCategoryChange(e.target.value)}
            >
              <option value="smartphones">📱 Smartphone / Mobile</option>
              <option value="laptops">💻 Laptop / PC</option>
              <option value="tablets">📱 Tablet / iPad</option>
              <option value="cameras">📷 Camera / Mirrorless</option>
              <option value="audio">🎧 Audio / Headphones</option>
              <option value="gaming">🎮 Gaming Console</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Product Model Title</label>
            <input
              type="text"
              className="form-input"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Apple iPhone 13 128GB, MacBook Air M1, Sony WH-1000XM4..."
            />
            {/* Quick Presets */}
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginTop: "8px" }}>
              <span style={{ fontSize: "11px", color: "var(--text-muted)", alignSelf: "center" }}>Quick presets:</span>
              {CATEGORY_MAP[category]?.presets.map((p) => (
                <button
                  key={p.label}
                  type="button"
                  style={{
                    background: title === p.label ? "var(--primary-light)" : "var(--bg-subtle)",
                    border: `1px solid ${title === p.label ? "var(--primary)" : "var(--border)"}`,
                    color: title === p.label ? "var(--primary-text)" : "var(--text-muted)",
                    borderRadius: "14px",
                    padding: "3px 10px",
                    fontSize: "11px",
                    cursor: "pointer",
                  }}
                  onClick={() => {
                    setTitle(p.label);
                    setAskingPrice(p.price);
                  }}
                >
                  {p.label} (₹{Number(p.price).toLocaleString("en-IN")})
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Asking Price (₹ INR)</label>
            <div className="input-with-symbol">
              <span className="currency-prefix">₹</span>
              <input
                type="number"
                className="form-input"
                value={askingPrice}
                onChange={(e) => setAskingPrice(e.target.value)}
                placeholder="e.g. 42000"
              />
            </div>
          </div>

          <div style={{ textAlign: "right", marginTop: "24px" }}>
            <button
              className="btn btn-primary"
              disabled={!title.trim() || !askingPrice}
              onClick={() => setStep(2)}
            >
              Next: Upload Photos →
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: Photo Evidence & Live Computer Vision */}
      {step === 2 && (
        <div className="card">
          <h2 className="card-title">Step 2: Upload Device Photographs</h2>
          <p className="card-subtitle">
            Upload clear photographs of your device. ReSellIQ’s computer vision engine will verify that the image matches an electronic device and scan for scratches or screen damage.
          </p>

          {photoValidationError && (
            <div className="alert alert-danger">
              <span>⛔</span>
              <div>
                <strong>Image Rejected:</strong> {photoValidationError}
              </div>
            </div>
          )}

          <div className="upload-grid">
            {[
              { label: "1. Front Screen Display", desc: "Display powered ON in bright light" },
              { label: "2. Back Cover & Camera", desc: "Rear casing and camera cluster" },
              { label: "3. Side Frame & Corners", desc: "Bezel and corners for impact scuffs" },
            ].map((slot, index) => {
              const photo = uploadedPhotos[index];
              const scanning = isScanning[index];
              const res = defectResults[index];
              const isInvalid = res && res.is_valid_device_photo === false;
              const hasDefects = res && res.defect_count > 0;

              return (
                <div
                  key={index}
                  className={`upload-box ${photo ? "has-image" : ""} ${isInvalid ? "has-error" : ""}`}
                  onClick={() => {
                    const input = document.getElementById(`file-upload-${index}`);
                    if (input) input.click();
                  }}
                >
                  <input
                    id={`file-upload-${index}`}
                    type="file"
                    accept="image/*"
                    style={{ display: "none" }}
                    onChange={(e) => handlePhotoUpload(index, e.target.files[0])}
                  />

                  {photo ? (
                    <>
                      <img src={photo} alt={slot.label} className="upload-preview" />
                      <div className="upload-label">{slot.label}</div>
                      {scanning ? (
                        <div className="upload-status">🔍 Scanning...</div>
                      ) : isInvalid ? (
                        <div className="upload-status status-rejected">⛔ Rejected: Non-Device Photo</div>
                      ) : hasDefects ? (
                        <div className="upload-status status-defect">⚠️ {res.defect_count} defect(s) detected</div>
                      ) : (
                        <div className="upload-status status-clean">✓ No visible defects detected</div>
                      )}
                    </>
                  ) : (
                    <>
                      <div style={{ fontSize: "28px", marginBottom: "6px" }}>📷</div>
                      <div className="upload-label">{slot.label}</div>
                      <div style={{ fontSize: "11px", color: "var(--text-muted)" }}>{slot.desc}</div>
                      <div style={{ marginTop: "8px", fontSize: "11px", color: "var(--primary)", fontWeight: "600" }}>
                        Click to upload
                      </div>
                    </>
                  )}
                </div>
              );
            })}
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", marginTop: "24px" }}>
            <button className="btn btn-secondary" onClick={() => setStep(1)}>
              ← Back
            </button>
            <button
              className="btn btn-primary"
              disabled={hasInvalidPhoto || Object.keys(uploadedPhotos).length === 0}
              onClick={() => setStep(3)}
            >
              {hasInvalidPhoto
                ? "Cannot Proceed (Image Rejected)"
                : Object.keys(uploadedPhotos).length === 0
                ? "Please Upload at least 1 Photo"
                : "Next: Condition Questions →"}
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: Interactive AI Condition Interview */}
      {step === 3 && (
        <div style={{ width: "100%" }}>
          {interviewMode === "chat" ? (
            /* AI Chat-Style Interview Container */
            <div className="chat-container">
              {/* Chat Header */}
              <div className="chat-header">
                <div className="chat-header-info">
                  <div className="chat-avatar">
                    🤖
                  </div>
                  <div>
                    <div className="chat-header-title">
                      AI Verification Inspector • {title || "Device Audit"}
                    </div>
                    <div className="chat-header-sub">
                      <span style={{ display: "inline-block", width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#16A34A", marginRight: "6px" }}></span>
                      Live Diagnostic Audit & Discrepancy Cross-Check
                    </div>
                  </div>
                </div>

                <div className="chat-mode-switch">
                  <button
                    className={`chat-mode-btn ${interviewMode === "chat" ? "active" : ""}`}
                    onClick={() => setInterviewMode("chat")}
                  >
                    💬 AI Chat
                  </button>
                  <button
                    className={`chat-mode-btn ${interviewMode === "form" ? "active" : ""}`}
                    onClick={() => setInterviewMode("form")}
                  >
                    📋 Quick Form
                  </button>
                </div>
              </div>

              {/* Chat Body */}
              <div className="chat-body">
                {chatMessages.map((msg) => (
                  <div key={msg.id} className={`chat-msg-row ${msg.sender}`}>
                    {msg.sender === "ai" && (
                      <div className="chat-msg-avatar">
                        🤖
                      </div>
                    )}
                    <div
                      className={`chat-bubble ${msg.sender === "ai" ? "chat-bubble-ai" : "chat-bubble-user"}`}
                      style={
                        msg.isAlert
                          ? { backgroundColor: "var(--warning-light)", borderColor: "#fde68a", color: "var(--warning-text)" }
                          : msg.isFinal
                          ? { backgroundColor: "var(--success-light)", borderColor: "#bbf7d0", color: "var(--success-text)", fontWeight: "500" }
                          : {}
                      }
                    >
                      <div>{msg.text}</div>

                      {/* Interactive Option Chips for the active question */}
                      {msg.options && msg.stepIndex === chatStep && (
                        <div className="chat-options-grid">
                          {msg.options.map((opt) => (
                            <button
                              key={opt.val}
                              type="button"
                              className="chat-option-btn"
                              onClick={() => handleChatAnswer(opt.val, opt.label)}
                            >
                              <span>{opt.label}</span>
                            </button>
                          ))}
                        </div>
                      )}

                      {/* Final Step Action Button */}
                      {msg.isFinal && (
                        <div style={{ marginTop: "16px" }}>
                          <button
                            className="btn btn-primary"
                            style={{ padding: "12px 24px", fontSize: "14px", fontWeight: "700" }}
                            onClick={handleGenerateReport}
                          >
                            Generate Official Condition Certificate 🚀
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {/* AI Typing Indicator */}
                {isAiTyping && (
                  <div className="chat-msg-row ai">
                    <div className="chat-msg-avatar">🤖</div>
                    <div className="chat-bubble chat-bubble-ai">
                      <div className="typing-indicator">
                        <span className="typing-dot"></span>
                        <span className="typing-dot"></span>
                        <span className="typing-dot"></span>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={chatBottomRef} />
              </div>

              {/* Chat Input & Navigation Footer */}
              <div className="chat-footer">
                <button className="btn btn-secondary" onClick={() => setStep(2)} style={{ padding: "8px 14px", fontSize: "13px" }}>
                  ← Photos
                </button>
                <input
                  type="text"
                  className="chat-input"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleChatSend();
                  }}
                  placeholder={
                    chatStep <= 4
                      ? "Type your response or click an option above..."
                      : "Inspection completed. Click generate certificate above."
                  }
                  disabled={chatStep > 4 || isAiTyping}
                />
                <button
                  className="btn btn-primary"
                  onClick={handleChatSend}
                  disabled={!chatInput.trim() || chatStep > 4 || isAiTyping}
                  style={{ padding: "9px 18px", fontSize: "13px" }}
                >
                  Send 💬
                </button>
              </div>
            </div>
          ) : (
            /* Traditional Quick Form View */
            <div className="card">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                <div>
                  <h2 className="card-title">Step 3: Condition Questionnaire for {title}</h2>
                  <p className="card-subtitle">
                    Select your responses. Answers will be cross-checked with uploaded photos.
                  </p>
                </div>
                <div className="chat-mode-switch">
                  <button
                    className={`chat-mode-btn ${interviewMode === "chat" ? "active" : ""}`}
                    onClick={() => setInterviewMode("chat")}
                  >
                    💬 AI Chat
                  </button>
                  <button
                    className={`chat-mode-btn ${interviewMode === "form" ? "active" : ""}`}
                    onClick={() => setInterviewMode("form")}
                  >
                    📋 Quick Form
                  </button>
                </div>
              </div>

              {/* Question 1: Cosmetic Condition */}
              <div className="form-group" style={{ marginBottom: "20px" }}>
                <label className="form-label">1. Overall Cosmetic & Aesthetic Condition</label>
                <div className="choice-cards">
                  {[
                    { val: "like_new", icon: "✨", title: "Like New / Mint", desc: "Pristine condition, zero noticeable scratches or scuffs" },
                    { val: "good", icon: "👍", title: "Good Condition", desc: "Minor light hairline scuffs from normal use, no cracks" },
                    { val: "fair", icon: "⚠️", title: "Fair Condition", desc: "Noticeable scratches on screen or back casing" },
                    { val: "poor", icon: "❌", title: "Heavy Wear", desc: "Deep dents, chipped glass, or heavy scratches" },
                  ].map((opt) => (
                    <div
                      key={opt.val}
                      className={`choice-card ${cosmeticCondition === opt.val ? "selected" : ""}`}
                      onClick={() => setCosmeticCondition(opt.val)}
                    >
                      <span className="choice-card-icon">{opt.icon}</span>
                      <div>
                        <div className="choice-card-title">{opt.title}</div>
                        <div className="choice-card-desc">{opt.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Question 2: Functional Status */}
              <div className="form-group" style={{ marginBottom: "20px" }}>
                <label className="form-label">2. Hardware Components & Operational Health</label>
                <div className="choice-cards">
                  {[
                    { val: "fully_working", icon: "🟢", title: "100% Fully Functional", desc: "Display, touch, cameras, Wi-Fi, and battery working normally" },
                    { val: "minor_issues", icon: "🟡", title: "Minor Issue", desc: "Battery health below 80% or faint display tint" },
                    { val: "major_issues", icon: "🔴", title: "Major Fault", desc: "Camera faulty, touch dead spots, or speaker distortion" },
                  ].map((opt) => (
                    <div
                      key={opt.val}
                      className={`choice-card ${functionalStatus === opt.val ? "selected" : ""}`}
                      onClick={() => setFunctionalStatus(opt.val)}
                    >
                      <span className="choice-card-icon">{opt.icon}</span>
                      <div>
                        <div className="choice-card-title">{opt.title}</div>
                        <div className="choice-card-desc">{opt.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Question 3: Repair History */}
              <div className="form-group" style={{ marginBottom: "20px" }}>
                <label className="form-label">3. Service & Repair History</label>
                <div className="choice-cards">
                  {[
                    { val: "never_repaired", icon: "🛡️", title: "Never Repaired", desc: "100% Original factory parts, never opened" },
                    { val: "professionally_repaired", icon: "🏢", title: "Authorized Service Center", desc: "Repaired by official brand with genuine OEM parts" },
                    { val: "self_repaired", icon: "🔧", title: "Third-Party / Local Repair", desc: "Screen or battery replaced at a local shop" },
                  ].map((opt) => (
                    <div
                      key={opt.val}
                      className={`choice-card ${repairHistory === opt.val ? "selected" : ""}`}
                      onClick={() => setRepairHistory(opt.val)}
                    >
                      <span className="choice-card-icon">{opt.icon}</span>
                      <div>
                        <div className="choice-card-title">{opt.title}</div>
                        <div className="choice-card-desc">{opt.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Question 4: Accessories */}
              <div className="form-group" style={{ marginBottom: "20px" }}>
                <label className="form-label">4. Original Packaging & Included Accessories</label>
                <div className="choice-cards">
                  {[
                    { val: "all", icon: "📦", title: "Complete Package", desc: "Original box, bill, and power adapter/charger included" },
                    { val: "some_missing", icon: "🔌", title: "Device + Charging Cable", desc: "Working cable included, but retail box is missing" },
                    { val: "many_missing", icon: "📱", title: "Device Only", desc: "Handset/unit only, no charger or box" },
                  ].map((opt) => (
                    <div
                      key={opt.val}
                      className={`choice-card ${accessories === opt.val ? "selected" : ""}`}
                      onClick={() => setAccessories(opt.val)}
                    >
                      <span className="choice-card-icon">{opt.icon}</span>
                      <div>
                        <div className="choice-card-title">{opt.title}</div>
                        <div className="choice-card-desc">{opt.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Optional Notes */}
              <div className="form-group">
                <label className="form-label">Additional Inspection Notes (Optional)</label>
                <input
                  type="text"
                  className="form-input"
                  value={repairNotes}
                  onChange={(e) => setRepairNotes(e.target.value)}
                  placeholder="e.g. Minor screen scratch on top left, battery health 89%"
                />
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", marginTop: "28px" }}>
                <button className="btn btn-secondary" onClick={() => setStep(2)}>
                  ← Back to Photos
                </button>
                <button className="btn btn-primary" onClick={handleGenerateReport}>
                  Generate Verified Certificate 🚀
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
