"""
Domain & Project Intelligence Module for AI/ML/Data Engineering.
Provides deep, industry-specific requirement matrices and high-vision Capstone Project Blueprints
extracted from 513+ production job descriptions (Qualcomm, JPMorgan, Mozilla, Nokia Bell Labs, Spotify, DataRobot, etc.).
"""

from typing import List, Dict, Any

DOMAIN_INTELLIGENCE_DATA: List[Dict[str, Any]] = [
    {
        "id": "agentic-ai",
        "title": "Agentic AI & Multi-Agent LLM Systems",
        "tagline": "Autonomous Workflow Orchestration, Deterministic Tool-Calling & LLMOps Evaluation",
        "icon": "Bot",
        "badge": "Highest Demand 2026",
        "target_roles": ["AI Engineer", "LLM Engineer", "GenAI Software Engineer", "Agent Architect"],
        "industry_context": {
            "summary": "Enterprises are moving beyond simple chatbots to multi-agent autonomous systems that execute multi-step workflows, query enterprise databases, and self-correct on failure.",
            "companies_hiring": ["Mozilla", "Capital.com", "DataRobot", "Jobright AI", "Cloudflare", "Qualcomm AI Hub"],
            "real_world_tasks": [
                "Building deterministic state machines for multi-agent workflows with human-in-the-loop approval gates.",
                "Designing semantic routing architectures to dispatch simple queries to local SLMs and complex reasoning to Frontier models.",
                "Engineering robust tool-calling layers with Pydantic JSON Schema validation, retry loops, and sandbox execution.",
                "Continuous automated regression testing of LLM output quality using LLM-as-a-judge frameworks."
            ]
        },
        "intern_junior_expectations": {
            "core_theories": [
                "ReAct Prompting & Plan-and-Solve architectures vs Finite State Machines (FSM).",
                "Context Window Management: Lost-in-the-middle phenomena, semantic chunking vs recursive chunking.",
                "Evaluation Triad: Groundedness (faithfulness), Context Relevance, Answer Relevance."
            ],
            "engineering_skills": [
                "LangGraph / Temporal for durable, checkpointed state execution and rollback.",
                "FastAPI + Async Streaming (SSE) for sub-second Time-To-First-Token (TTFT).",
                "Vector Databases + Hybrid Search (BM25 + Dense Embeddings + Cross-Encoder Reranking).",
                "DeepEval / TruLens / Ragas for automated CI/CD metric pipelines."
            ],
            "cost_latency_tradeoffs": [
                "Implementing semantic caching (Redis / GPTCache) to achieve 60-80% cost reduction on recurring queries.",
                "Prompt token minimization and structured output schemas to prevent token budget blowouts."
            ]
        },
        "capstone_blueprint": {
            "project_name": "SentinEL: Enterprise Multi-Agent Regulatory Compliance & Code Governance Orchestrator",
            "value_prop": "An autonomous multi-agent system that audits codebase PRs against security, architectural guidelines, and data compliance standards with deterministic validation.",
            "core_problem": "Human code reviews for compliance and security are slow and error-prone, while standard LLMs hallucinate rules or fail on complex multi-file dependencies.",
            "system_architecture": [
                "1. Triage Agent: Uses Tree-Sitter AST parsing to extract modified symbol graphs and routes to specialized worker agents.",
                "2. Static Security Agent: Executes Semgrep rules and maps vulnerabilities to CVE databases.",
                "3. Policy Compliance Agent: Uses Hybrid RAG over company compliance documentation to verify data privacy (GDPR/HIPAA).",
                "4. Arbiter & Synthesis Agent: Evaluates confidence scores, aggregates findings into structured PR comments, and alerts human reviewers when confidence is below 85%."
            ],
            "key_metrics_to_show": [
                "Context Precision: > 92% on regulatory benchmark queries.",
                "False Positive Rate: < 4% via deterministic AST verification loop.",
                "P95 Review Latency: < 3.2s via parallel agent execution."
            ],
            "standout_factor": "Shows you understand production failure modes: you didn't just build a toy prompt wrapper, you engineered state persistence, deterministic sandboxing, and automated evaluation metrics."
        }
    },
    {
        "id": "computer-vision",
        "title": "Computer Vision & Edge Multimodal AI",
        "tagline": "Real-Time Streaming Inference, Low-Latency Hardware Acceleration & Edge Video Analytics",
        "icon": "Eye",
        "badge": "High Hardware Demand",
        "target_roles": ["Computer Vision Engineer", "Edge AI Engineer", "Robotics Perception Specialist"],
        "industry_context": {
            "summary": "Deploying perception models to resource-constrained edge hardware for autonomous navigation, industrial defect inspection, and smart traffic monitoring.",
            "companies_hiring": ["Qualcomm AI Hub", "Nokia Bell Labs", "Liebherr", "Skyworks", "BAM Careers"],
            "real_world_tasks": [
                "Optimizing YOLO / ViT architectures for low-power edge chips using INT8/FP16 quantization.",
                "Building zero-drop RTSP/WebRTC multi-stream video decoding and batching pipelines.",
                "Implementing multi-object tracking (MOT) across non-overlapping multi-camera topologies.",
                "Handling domain shift (adverse weather, lighting conditions) using synthetic data augmentation."
            ]
        },
        "intern_junior_expectations": {
            "core_theories": [
                "Object Detection paradigms: Two-stage (Faster R-CNN) vs One-stage (YOLO, RT-DETR).",
                "Model Quantization (PTQ vs QAT) and pruning trade-offs between mAP and latency.",
                "Kalman Filters, Hungarian Algorithm, and ByteTrack association logic."
            ],
            "engineering_skills": [
                "TensorRT / ONNX Runtime / OpenVINO optimization and engine compilation.",
                "C++ / Python bindings with OpenCV, CUDA acceleration, and PyTorch C++ API (LibTorch).",
                "GStreamer / FFmpeg for low-latency hardware-accelerated video streaming queues.",
                "Triton Inference Server for dynamic batching on GPU clusters."
            ],
            "cost_latency_tradeoffs": [
                "Frame skipping and spatial ROI cropping to reduce compute by 40% without losing detection accuracy."
            ]
        },
        "capstone_blueprint": {
            "project_name": "VisionFlow: Zero-Latency Multi-Camera Smart Traffic & Incident Orchestrator",
            "value_prop": "An end-to-end edge-to-cloud computer vision pipeline processing 8+ simultaneous RTSP 1080p camera streams to detect traffic collisions and flow bottlenecks in real-time.",
            "core_problem": "Raw video streaming floods network bandwidth, and centralized cloud inference incurs high latency and bandwidth costs.",
            "system_architecture": [
                "1. Edge Ingestion: Hardware-accelerated GStreamer pipeline decoding RTSP streams with zero-copy shared memory.",
                "2. TensorRT Inference Engine: Custom-quantized YOLOv10-INT8 achieving 120 FPS per GPU.",
                "3. Cross-Camera Tracking: ByteTrack + ReID embeddings with geospatial spatial consistency filtering.",
                "4. Anomaly Alert Gateway: Publishes incident metadata via MQTT / WebSocket to a real-time Web dashboard."
            ],
            "key_metrics_to_show": [
                "End-to-End Latency: < 45ms per frame at 1080p resolution.",
                "Edge Memory Footprint: < 1.8 GB VRAM across 8 concurrent streams.",
                "mAP@50-95: 84.6% on challenging benchmark datasets."
            ],
            "standout_factor": "Demonstrates hardware acceleration mastery, streaming pipeline stability, and understanding of edge-cloud partitioning."
        }
    },
    {
        "id": "healthcare-ai",
        "title": "Healthcare & Clinical Life Sciences AI",
        "tagline": "Multimodal Biomedical Data, Citation-Verified Clinical RAG & HIPAA-Compliant Pipelines",
        "icon": "HeartPulse",
        "badge": "High Impact & Strict Regs",
        "target_roles": ["Healthcare Data Scientist", "Clinical AI Engineer", "Bioinformatics Specialist"],
        "industry_context": {
            "summary": "Developing decision support systems that assist clinicians in interpreting electronic health records (EHR), medical imaging, and genomics data while adhering to rigorous regulatory compliance.",
            "companies_hiring": ["Leiden University", "Cinq Care", "Eurofins", "KIS Solutions"],
            "real_world_tasks": [
                "Extracting structured clinical entities from unstructured doctor notes using clinical NER models.",
                "Building citation-grounded RAG systems over medical literature (PubMed, UpToDate) with strict provenance verification.",
                "Implementing de-identification and privacy-preserving data masking pipelines adhering to HIPAA Safe Harbor.",
                "Calibrating model uncertainty to prevent over-confident incorrect diagnoses."
            ]
        },
        "intern_junior_expectations": {
            "core_theories": [
                "Biomedical schemas: FHIR / HL7 standard data models and DICOM imaging metadata.",
                "Sensitivity vs Specificity trade-offs and ROC-AUC under extreme diagnostic class imbalance.",
                "Conformal Prediction for distribution-free uncertainty intervals."
            ],
            "engineering_skills": [
                "BioBERT / ClinicalBERT and specialized BioGPT embeddings.",
                "Differential privacy techniques and automated PII/PHI redaction with Microsoft Presidio.",
                "PostgreSQL / DuckDB with columnar analytical query optimization for longitudinal patient records."
            ],
            "cost_latency_tradeoffs": [
                "Prioritizing exact recall over raw speed; implementing double-check verification loops."
            ]
        },
        "capstone_blueprint": {
            "project_name": "ClinicaGrounded: Citation-Verified Multimodal Diagnostic Decision Support Copilot",
            "value_prop": "A clinical assistant that ingests patient FHIR records and lab results to synthesize diagnostic recommendations accompanied by verifiable PubMed citations and calibrated uncertainty scores.",
            "core_problem": "Clinicians cannot trust generic AI due to hallucination risks and lack of provenance back to peer-reviewed guidelines.",
            "system_architecture": [
                "1. FHIR Data Normalizer: Ingests patient observations and redacts all PHI before inference.",
                "2. Knowledge Retrieval Engine: Semantic search over 2M+ PubMed Central open-access papers with MeSH term expansion.",
                "3. Grounded Synthesis Engine: Generates clinical differential diagnoses with exact sentence-level citation markers.",
                "4. Provenance Validator: A secondary NLI (Natural Language Inference) verifier that checks if each generated sentence is strictly entailed by the cited literature."
            ],
            "key_metrics_to_show": [
                "Citation Entailment Score: > 96.5% validated via NLI verification loop.",
                "Zero Hallucinated Citations: 100% verification against PubMed PMID registry.",
                "PHI Leakage Rate: 0.00% on benchmark medical notes."
            ],
            "standout_factor": "Shows profound respect for safety-critical domain requirements, privacy compliance, and mathematical uncertainty quantification."
        }
    },
    {
        "id": "fintech-ai",
        "title": "Fintech, Fraud Prevention & Open Banking AI",
        "tagline": "Graph Neural Networks, Real-Time Streaming Feature Stores & Sub-50ms Transaction Sentinel",
        "icon": "CreditCard",
        "badge": "Sub-50ms Latency SLA",
        "target_roles": ["Fintech ML Engineer", "Fraud Risk Data Scientist", "Quantitative Systems Engineer"],
        "industry_context": {
            "summary": "Building ultra-low-latency real-time fraud detection, credit scoring, and open banking payment routing algorithms under strict financial auditability.",
            "companies_hiring": ["Frost Bank", "JPMorgan Chase", "Capital.com", "BT Group", "ENGIE"],
            "real_world_tasks": [
                "Engineering real-time streaming feature pipelines (e.g., transaction velocity, sliding window aggregations) via Kafka/Flink.",
                "Constructing heterogeneous transaction graph networks to detect organized fraud rings and synthetic identities.",
                "Producing regulatory-compliant explainability reports (SHAP values, reason codes) for declined transactions."
            ]
        },
        "intern_junior_expectations": {
            "core_theories": [
                "Imbalanced Learning: SMOTE, focal loss, precision-recall curve optimization at 0.01% positive rate.",
                "Graph Convolutional Networks (GCN / GraphSAGE) and temporal graph random walks.",
                "Model Explainability: Global vs Local feature attributions (TreeSHAP)."
            ],
            "engineering_skills": [
                "Feature Stores (Feast / Hopsworks) for online (Redis) vs offline (Snowflake/BigQuery) consistency.",
                "LightGBM / XGBoost / CatBoost optimized inference with ONNX or Treelite.",
                "Apache Kafka / Redpanda for event-driven streaming ingestion."
            ],
            "cost_latency_tradeoffs": [
                "Two-tier scoring: Tier-1 Tree model (< 10ms) filters 99% of normal traffic; Tier-2 GNN model executes on suspicious subset."
            ]
        },
        "capstone_blueprint": {
            "project_name": "GraphSentinel: Real-Time Streaming Graph Neural Network Fraud & AML Sentinel",
            "value_prop": "A high-throughput streaming fraud engine that combines transactional feature stores with dynamic Graph Neural Networks to detect synthetic identity theft in under 35ms.",
            "core_problem": "Traditional rule-based fraud engines miss complex multi-hop collusion rings and suffer from high false positive rates that degrade customer trust.",
            "system_architecture": [
                "1. Event Ingestion: Kafka stream ingesting 10,000+ transaction events/sec.",
                "2. Online Feature Pipeline: Feast + Redis updating 1-minute, 1-hour, and 24-hour velocity aggregations in sub-5ms.",
                "3. Heterogeneous Graph Builder: Dynamic node-edge creation linking IP, device fingerprint, bank card, and merchant ID.",
                "4. Fast Inference Ensemble: Treelite-compiled LightGBM + GraphSAGE embedding classifier running concurrently with SHAP explanation generation."
            ],
            "key_metrics_to_show": [
                "P99 End-to-End Latency: < 32ms under 5,000 TPS load.",
                "AUC-PR: 0.89 on 1:1000 imbalanced transaction dataset.",
                "Explainability SLA: 100% transactions have top-3 regulatory reason codes generated."
            ],
            "standout_factor": "Proves you can build distributed streaming data systems, handle extreme class imbalance, and meet bank-grade latency SLAs."
        }
    },
    {
        "id": "mlops-platform",
        "title": "Cloud Infrastructure & Production MLOps Platforms",
        "tagline": "High-Throughput LLM Serving, Distributed GPU Autoscaling & Self-Healing Inference Gateways",
        "icon": "Cpu",
        "badge": "High Infrastructure Value",
        "target_roles": ["MLOps Engineer", "Platform Engineer", "Distributed Systems Engineer"],
        "industry_context": {
            "summary": "Architecting reliable, scalable infrastructure to train, evaluate, and serve ML models and LLMs with maximum GPU utilization and zero downtime.",
            "companies_hiring": ["Cloudflare", "Spotify", "DataRobot", "Qualcomm", "BT Group"],
            "real_world_tasks": [
                "Setting up high-throughput LLM serving clusters using vLLM, PagedAttention, and Tensor Parallelism.",
                "Implementing canary deployments, shadow traffic testing, and automated rollbacks on model drift.",
                "Building automated model registries and metadata lineage tracking.",
                "Monitoring inference drift, latency percentiles (P95/P99), and GPU memory saturation."
            ]
        },
        "intern_junior_expectations": {
            "core_theories": [
                "Memory bandwidth vs Compute bound operations in LLM inference (KV-Cache bottleneck).",
                "Continuous Batching vs Static Batching; Speculative Decoding mechanics.",
                "Data Drift (Kolmogorov-Smirnov test, PSI) vs Concept Drift."
            ],
            "engineering_skills": [
                "Docker, Kubernetes (K8s), Helm charts, GPU operator configuration.",
                "vLLM, TGI, Triton Inference Server, Ray Core & Ray Serve.",
                "Prometheus, Grafana, OpenTelemetry instrumentation for custom ML metrics.",
                "CI/CD with GitHub Actions, CML, and Terraform for Infrastructure as Code (IaC)."
            ],
            "cost_latency_tradeoffs": [
                "Dynamic autoscaling from 0 to N nodes based on queue depth rather than raw CPU/GPU load."
            ]
        },
        "capstone_blueprint": {
            "project_name": "ApexServe: Self-Healing High-Throughput LLM Gateway with Speculative Routing & Drift Guard",
            "value_prop": "A production-grade LLM inference gateway and autoscaling orchestrator featuring dynamic request batching, speculative decoding, and automated canary rollbacks upon drift detection.",
            "core_problem": "LLM serving costs are exorbitant, and naive deployments crash under traffic bursts or silently degrade when input distributions drift.",
            "system_architecture": [
                "1. Intelligent Gateway: Reverse proxy written in Go / FastAPI that balances requests across heterogeneous GPU clusters.",
                "2. Dynamic Speculative Engine: Uses small draft model (1B) + target model (8B) to double token throughput per GPU.",
                "3. Real-Time Telemetry: OpenTelemetry exporter sending TTFT, TPS, and GPU KV-Cache utilization to Prometheus.",
                "4. Drift Sentinel: Continuously computes Population Stability Index (PSI) and triggers automated canary traffic shift if quality degrades."
            ],
            "key_metrics_to_show": [
                "Throughput Improvement: 2.3x higher Tokens/Sec per GPU dollar via speculative decoding.",
                "Zero-Downtime Rollback: Automated rollback within 15 seconds of detected drift.",
                "P99 Queue Latency: < 80ms under simulated peak load."
            ],
            "standout_factor": "Highlights systems-level thinking, deep understanding of GPU memory architectures, and production resilience."
        }
    },
    {
        "id": "search-rec",
        "title": "Intelligent Search, Recommendation & IR",
        "tagline": "Two-Stage Hybrid Search, RRF Fusion, Cross-Encoder Reranking & Multi-Task Ranking",
        "icon": "Search",
        "badge": "Direct Business Revenue",
        "target_roles": ["Search Engineer", "Recommendation System Data Scientist", "IR Specialist"],
        "industry_context": {
            "summary": "Building modern information retrieval and recommendation systems that power product discovery, content feeds, and personalized experiences.",
            "companies_hiring": ["Spotify", "Jobright", "Rippling", "Mozilla"],
            "real_world_tasks": [
                "Implementing hybrid search engines that combine lexical BM25 matching with dense neural vector embeddings.",
                "Developing multi-stage ranking pipelines (Candidate Generation -> ANN -> Heavy Reranker).",
                "Solving cold-start problems and designing exploration vs exploitation strategies (Multi-Armed Bandits).",
                "Building real-time user engagement feedback loops to update user preference vectors."
            ]
        },
        "intern_junior_expectations": {
            "core_theories": [
                "Two-Tower Neural Networks (Query Tower & Item Tower) for embedding representation.",
                "Approximate Nearest Neighbor (ANN) index algorithms: HNSW, IVFPQ.",
                "Ranking Metrics: NDCG@k, MRR@k, Precision@k, Recall@k."
            ],
            "engineering_skills": [
                "Elasticsearch / OpenSearch / Qdrant / Milvus for large-scale hybrid vector indexing.",
                "Reciprocal Rank Fusion (RRF) and Cross-Encoder (e.g. BGE-Reranker) implementation.",
                "Feature engineering for sequential user clickstream actions."
            ],
            "cost_latency_tradeoffs": [
                "Hierarchical filtering: Fast candidate retrieval (top 1000 in 5ms) -> ANN ranking (top 100 in 15ms) -> Deep cross-encoder (top 10 in 25ms)."
            ]
        },
        "capstone_blueprint": {
            "project_name": "NexusRank: Two-Stage Hybrid Semantic Search & Personalization Engine with Real-Time Feedback",
            "value_prop": "A high-performance search and recommendation engine combining sparse BM25, dense neural vectors, and real-time clickstream bandit adaptation for personalized content retrieval.",
            "core_problem": "Pure vector search suffers from exact keyword failure (part numbers, acronyms), while pure keyword search fails at semantic understanding.",
            "system_architecture": [
                "1. Dual Indexing Layer: Qdrant vector store + OpenSearch lexical inverted index with automated sync.",
                "2. Fusion Pipeline: Reciprocal Rank Fusion (RRF) blending dense and sparse scores with learned weighting.",
                "3. Cross-Encoder Reranker: ONNX-accelerated MiniLM Cross-Encoder reranking top-50 candidates in under 18ms.",
                "4. Contextual Bandit Feedback: Updates user session affinity vectors in Redis after every interaction."
            ],
            "key_metrics_to_show": [
                "NDCG@10: 0.884 (vs 0.692 for vanilla vector search).",
                "Search P95 Latency: < 42ms on a 500,000 document index.",
                "Zero Keyword Misses: 100% exact match recall on technical domain jargon."
            ],
            "standout_factor": "Demonstrates you know how tech giants actually build production search engines rather than relying on basic vector cosine similarity."
        }
    }
]
