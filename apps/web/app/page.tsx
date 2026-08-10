'use client';

import React, { useState, useEffect } from 'react';
import {
  Activity,
  Database,
  Cpu,
  Layers,
  CheckCircle,
  Search,
  ArrowUpRight,
  TrendingUp,
  ExternalLink,
  Briefcase,
  MapPin,
  Building2,
  Lock,
  X,
  Filter,
  DollarSign,
  Award,
  Sparkles,
  ShieldCheck,
  Globe,
  Clock,
  BookOpen,
} from 'lucide-react';

interface DataFreshness {
  total_jobs: number;
  active_jobs: number;
  analyzed_jobs: number;
  latest_job_crawled_at: string | null;
}

interface SkillStat {
  name: string;
  category: string;
  count: number;
  share: number;
  required_count: number;
  preferred_count: number;
}

interface JobSkill {
  name: string;
  requirement_type?: string;
  category?: string;
  evidence_text?: string;
}

interface JobItem {
  id: number | string;
  title: string;
  company_name: string;
  company_domain?: string;
  canonical_url: string;
  location: string;
  salary_range?: string;
  description_text: string;
  posted_time_ago: string;
  posted_at?: string | null;
  role_family: string;
  seniority: string;
  is_relevant: boolean;
  relevance_reason: string | null;
  ingestion_stage?: string;
  skills: JobSkill[];
  sections?: {
    overview?: string;
    team_challenge?: string;
    responsibilities?: string[];
    requirements?: string[];
    salary_info?: string[];
  };
}

const ROLES = ['AI Engineer', 'ML Engineer', 'MLOps Engineer', 'Data Scientist'];

const MULTI_SOURCE_JOBS: JobItem[] = [
  {
    id: 1,
    title: 'Software Engineer, AI/ML Infrastructure (US-Based)',
    company_name: 'Thumbtack',
    company_domain: 'thumbtack.com',
    canonical_url: 'https://jobs.ashbyhq.com/thumbtack/3efb1a7b-cfaf-475a-86a9-abff37581b4b/application',
    location: 'United States (Remote)',
    salary_range: '$145,400 - $188,100 / year',
    posted_time_ago: '8 hours ago',
    ingestion_stage: '2-Stage Deep Crawled (Ashby ATS Target)',
    description_text: `Thumbtack helps millions of people confidently care for their homes. Thumbtack is the one app you need to take care of and improve your home — from personalized guidance to AI tools and a best-in-class hiring experience.

About the Machine Learning Infrastructure Team:
At Thumbtack, our challenges span a wide range of areas, including search, recommendations, matchmaking, pricing, safety, content generation, fraud detection, and more. The ML Infrastructure team is responsible for centralizing, standardizing and evolving AI/ML infrastructure that enables these experiences.

The Challenge:
As a Software Engineer on the ML Infrastructure team, you will work closely with product and platform engineering teams to build and evolve core AI platform capabilities. You will help design and improve systems that allow teams to develop, run, and scale GenAI-powered applications in production.`,
    posted_at: new Date().toISOString(),
    role_family: 'AI Engineer',
    seniority: 'Entry Level',
    is_relevant: true,
    relevance_reason: 'Core AI Platform & ML Infrastructure engineering role matching technical criteria.',
    skills: [
      { name: 'Python', requirement_type: 'required', category: 'language', evidence_text: 'Primary stack includes Go and Python' },
      { name: 'Go', requirement_type: 'required', category: 'language', evidence_text: 'Primary stack includes Go and Python' },
      { name: 'PyTorch', requirement_type: 'required', category: 'ml_framework', evidence_text: 'Traditional ML model training and serving systems' },
      { name: 'Postgres', requirement_type: 'required', category: 'database', evidence_text: 'Experience working with relational databases such as Postgres' },
      { name: 'DynamoDB', requirement_type: 'preferred', category: 'database', evidence_text: 'NoSQL databases such as DynamoDB' },
      { name: 'AI Coding Tools', requirement_type: 'required', category: 'tool', evidence_text: 'Demonstrated ability to use AI coding tools in day-to-day workflows' },
    ],
    sections: {
      overview:
        'Thumbtack is a home services platform connecting millions of homeowners with local service providers. Founded in 2008 in San Francisco, CA with 1,000-5,000 employees.',
      team_challenge:
        'The ML Infrastructure team builds scalable, high-performance platform capabilities for GenAI applications, model training/serving, feature workflows, and orchestration.',
      responsibilities: [
        'Build and evolve core AI platform capabilities that enable teams to develop, run, and scale GenAI-powered applications across Thumbtack.',
        'Contribute to the design, development, and deployment of scalable tools and infrastructure to support applied scientists (ML model serving, feature workflows, CI/CD, orchestration).',
        'Work hands on across the stack, from backend services and execution infrastructure to integrations with AI models and tooling.',
        'Partner with senior engineers to evaluate next-generation AI infrastructure frameworks and tools.',
        'Drive projects to completion with a strong focus on business impact and measurable outcomes.',
      ],
      requirements: [
        '1 to 3 years of professional software engineering experience.',
        'Strong fundamentals in data structures, algorithms, and software design.',
        'Proficiency in Go and Python.',
        'Experience with relational or NoSQL databases such as Postgres or DynamoDB.',
        'Demonstrated ability to use AI coding tools in day-to-day workflows and validate AI-generated output.',
        'Comfort operating in a fast-paced environment with ambiguity and a strong bias to action.',
      ],
      salary_info: [
        'San Francisco / Bay Area, San Jose, NYC, Seattle metros: $145,400 - $188,100 / yr',
        'Austin TX, Washington DC, CA, MA, NJ, WA states: $130,900 - $169,400 / yr',
        'All other US locations: $123,300 - $159,500 / yr',
      ],
    },
  },
  {
    id: 2,
    title: 'Artificial Intelligence Intern',
    company_name: 'Muro AI',
    company_domain: 'muro.ai',
    canonical_url: 'https://www.linkedin.com/jobs/view/4446448878',
    location: 'San Francisco Bay Area (Onsite)',
    salary_range: 'Competitive Intern Stipend + H1B Eligibility',
    posted_time_ago: '3 days ago',
    ingestion_stage: '2-Stage Deep Crawled (LinkedIn Direct)',
    description_text:
      'Muro AI builds AI agents for general contractor companies to automate pre-construction activities and streamline complex workflows. As an Artificial Intelligence Intern, you will support the development of AI agents and collaborate with engineers and data scientists.',
    posted_at: new Date().toISOString(),
    role_family: 'AI Engineer',
    seniority: 'Intern',
    is_relevant: true,
    relevance_reason: 'AI Agent & LLM internship role',
    skills: [
      { name: 'Python', requirement_type: 'required' },
      { name: 'Machine Learning', requirement_type: 'required' },
      { name: 'Git', requirement_type: 'required' },
      { name: 'Prompt Engineering', requirement_type: 'required' },
    ],
    sections: {
      overview: 'Muro AI builds AI agents for General Contractors to automate pre-construction activities. Founded in 2023 in New York.',
      responsibilities: [
        'Support the development and improvement of AI agents used in pre-construction workflows.',
        'Help design and implement ML models, write & test Python code, and analyze data.',
        'Collaborate with engineers and data scientists to prototype features.',
      ],
      requirements: [
        'Currently pursuing or completed degree in Computer Science, Data Science, or Engineering.',
        'Exposure to Machine Learning, Python, and Git version control.',
        'Interest in applying AI to construction, architecture, or operations.',
      ],
    },
  },
  {
    id: 3,
    title: 'Senior AI Engineer - Workers AI',
    company_name: 'Cloudflare',
    company_domain: 'cloudflare.com',
    canonical_url: 'https://boards.greenhouse.io/cloudflare/jobs/40101',
    location: 'San Francisco, CA',
    salary_range: '$170,000 - $220,000 / year',
    posted_time_ago: '1 day ago',
    ingestion_stage: '1-Pass Direct Greenhouse REST API',
    description_text:
      'Architecting distributed inference pipelines on Cloudflare Workers AI. Deep experience with C++, CUDA, PyTorch, Docker, Kubernetes, and LLM serving.',
    posted_at: new Date().toISOString(),
    role_family: 'AI Engineer',
    seniority: 'Senior',
    is_relevant: true,
    relevance_reason: 'High-scale inference engineering role',
    skills: [
      { name: 'PyTorch', requirement_type: 'required' },
      { name: 'CUDA', requirement_type: 'required' },
      { name: 'Docker', requirement_type: 'required' },
      { name: 'Kubernetes', requirement_type: 'required' },
    ],
    sections: {
      overview: 'Cloudflare is a global cloud platform providing web security, performance, and Workers AI serverless GPU inference.',
      responsibilities: ['Build distributed GPU inference pipelines', 'Optimize LLM serving latency on edge nodes', 'Deploy containerized ML worker nodes'],
      requirements: ['5+ YOE in C++/Python', 'PyTorch & CUDA expertise', 'Kubernetes & Docker container orchestration'],
    },
  },
  {
    id: 4,
    title: 'Lead Machine Learning Engineer',
    company_name: 'Spotify',
    company_domain: 'spotify.com',
    canonical_url: 'https://jobs.lever.co/spotify/80102',
    location: 'Stockholm, Sweden / Remote',
    salary_range: '€110,000 - €145,000 / year',
    posted_time_ago: '2 days ago',
    ingestion_stage: '1-Pass Direct Lever REST API',
    description_text:
      'Lead personalization algorithms and ML recommender systems at Spotify. Experience with PyTorch, Ray, Scikit-learn, BigQuery, and scalable feature stores.',
    posted_at: new Date().toISOString(),
    role_family: 'ML Engineer',
    seniority: 'Lead',
    is_relevant: true,
    relevance_reason: 'Recommender & personalization ML lead role',
    skills: [
      { name: 'PyTorch', requirement_type: 'required' },
      { name: 'Ray', requirement_type: 'required' },
      { name: 'Python', requirement_type: 'required' },
      { name: 'BigQuery', requirement_type: 'preferred' },
    ],
    sections: {
      overview: 'Spotify is the world’s largest audio streaming platform serving over 600 million active listeners worldwide.',
      responsibilities: ['Lead ML recommendation algorithms', 'Design scalable feature pipelines', 'Mentor ML engineers on model evaluation'],
      requirements: ['6+ YOE in Machine Learning', 'Strong background in Recommendation Systems', 'Proficiency in PyTorch and Distributed Computing'],
    },
  },
  {
    id: 5,
    title: 'Agentic AI MLOps Engineer',
    company_name: 'DataRobot',
    company_domain: 'datarobot.com',
    canonical_url: 'https://datarobot.wd1.myworkdayjobs.com/DataRobot_External_Careers/job/Boston-MA/Agentic-AI-Intern_R-102729',
    location: 'Boston, MA (Hybrid)',
    salary_range: '$150,000 - $195,000 / year',
    posted_time_ago: '5 hours ago',
    ingestion_stage: '1-Pass Direct Workday REST API',
    description_text:
      'Build automated MLOps pipelines and LLM evaluation benchmarks for enterprise AI agents. Tech stack: Python, LangChain, Kubernetes, MLflow, Prometheus.',
    posted_at: new Date().toISOString(),
    role_family: 'MLOps Engineer',
    seniority: 'Mid-Senior',
    is_relevant: true,
    relevance_reason: 'Agentic MLOps & LLM evaluation pipeline role',
    skills: [
      { name: 'Kubernetes', requirement_type: 'required' },
      { name: 'LangChain', requirement_type: 'required' },
      { name: 'MLflow', requirement_type: 'required' },
      { name: 'Prometheus', requirement_type: 'preferred' },
    ],
    sections: {
      overview: 'DataRobot provides enterprise AI platforms automating ML model lifecycle management, governance, and deployment.',
      responsibilities: ['Build MLOps pipelines for LLM agents', 'Configure Prometheus observability & MLflow model registry', 'Automate CI/CD test gates'],
      requirements: ['3+ YOE in MLOps/DevOps', 'Kubernetes, Docker, Python', 'Experience with MLflow and LangChain'],
    },
  },
  {
    id: 6,
    title: 'AI Team Leader & Branch Manager',
    company_name: 'ACWORKS VIETNAM',
    company_domain: 'topcv.vn',
    canonical_url: 'https://www.topcv.vn/viec-lam/ai-team-leader-branch-manager-ha-noi/2121776.html',
    location: 'Hà Nội, Vietnam',
    salary_range: '35,000,000 - 50,000,000 VND / tháng',
    posted_time_ago: '1 day ago',
    ingestion_stage: 'TopCV DOM & JSON-LD Scraper',
    description_text:
      'Quản lý và định hướng nghiên cứu các giải pháp AI (Computer Vision, Generative AI). Thành thạo Python, PyTorch, OpenCV, Docker, triển khai Model lên Cloud.',
    posted_at: new Date().toISOString(),
    role_family: 'AI Engineer',
    seniority: 'Lead',
    is_relevant: true,
    relevance_reason: 'AI Team Leader role in Vietnam Market',
    skills: [
      { name: 'Python', requirement_type: 'required' },
      { name: 'PyTorch', requirement_type: 'required' },
      { name: 'Computer Vision', requirement_type: 'required' },
      { name: 'Docker', requirement_type: 'required' },
    ],
    sections: {
      overview: 'ACWORKS VIETNAM là công ty công nghệ chuyên nghiên cứu các giải pháp AI thế hệ mới (GenAI, Image Processing) có trụ sở tại Hà Nội.',
      responsibilities: ['Lãnh đạo team AI R&D 10 nhân sự', 'Xây dựng giải pháp GenAI & Computer Vision', 'Quản lý dự án & triển khai Cloud'],
      requirements: ['4+ năm kinh nghiệm lập trình AI', 'Thành thạo Python, PyTorch, Docker', 'Khả năng đọc hiểu tài liệu tiếng Anh/tiếng Nhật'],
    },
  },
  {
    id: 7,
    title: 'AI R&D Engineering Co-op',
    company_name: 'Nokia Bell Labs',
    company_domain: 'foorilla.com',
    canonical_url: 'https://foorilla.com/hiring/jobs/redirect-nokia-101',
    location: 'Basking Ridge, NJ (Remote Eligible)',
    salary_range: '$45 - $55 / hour',
    posted_time_ago: '4 days ago',
    ingestion_stage: 'Foorilla HTMX Topic Ingestion',
    description_text:
      'Research next-gen network AI algorithms with Nokia Bell Labs. Hands-on experience with PyTorch, TensorFlow, Python, and C++ for distributed network ML.',
    posted_at: new Date().toISOString(),
    role_family: 'AI Engineer',
    seniority: 'Junior / Co-op',
    is_relevant: true,
    relevance_reason: 'R&D AI Engineering co-op role',
    skills: [
      { name: 'PyTorch', requirement_type: 'required' },
      { name: 'TensorFlow', requirement_type: 'required' },
      { name: 'Python', requirement_type: 'required' },
    ],
    sections: {
      overview: 'Nokia Bell Labs is a world-renowned industrial research institute inventing technologies at the intersection of AI, networking, and physics.',
      responsibilities: ['Prototype novel network AI algorithms', 'Train PyTorch models on distributed GPU clusters', 'Publish research findings'],
      requirements: ['Currently enrolled in MS/PhD in CS/ECE', 'PyTorch/TensorFlow expertise', 'Strong linear algebra & calculus fundamentals'],
    },
  },
  {
    id: 8,
    title: 'AI R&D Co-op (Account Locked)',
    company_name: 'Foorilla Partner',
    company_domain: 'foorilla.com',
    canonical_url: 'https://foorilla.com/account/login/?next=/hiring/jobs/1029',
    location: 'Remote (US)',
    salary_range: 'Subscription Required',
    posted_time_ago: '6 days ago',
    ingestion_stage: 'Paywall Audit Logging (0 Token)',
    description_text: 'Requires user authentication / paywall subscription to view full listing content.',
    posted_at: new Date().toISOString(),
    role_family: 'AI Engineer',
    seniority: 'Junior',
    is_relevant: false,
    relevance_reason: 'Paywall / Login wall detected',
    skills: [],
  },
];

const SAMPLE_SKILLS: Record<string, SkillStat[]> = {
  'AI Engineer': [
    { name: 'Python', category: 'language', count: 6, share: 1.0, required_count: 6, preferred_count: 0 },
    { name: 'PyTorch', category: 'ml_framework', count: 5, share: 0.83, required_count: 4, preferred_count: 1 },
    { name: 'Go', category: 'language', count: 3, share: 0.5, required_count: 3, preferred_count: 0 },
    { name: 'LangChain', category: 'framework', count: 4, share: 0.66, required_count: 3, preferred_count: 1 },
    { name: 'FastAPI', category: 'framework', count: 3, share: 0.5, required_count: 2, preferred_count: 1 },
    { name: 'Kubernetes', category: 'devops', count: 4, share: 0.66, required_count: 4, preferred_count: 0 },
    { name: 'Docker', category: 'devops', count: 5, share: 0.83, required_count: 5, preferred_count: 0 },
    { name: 'PostgreSQL / pgvector', category: 'database', count: 3, share: 0.5, required_count: 3, preferred_count: 0 },
  ],
  'MLOps Engineer': [
    { name: 'Kubernetes', category: 'devops', count: 4, share: 1.0, required_count: 4, preferred_count: 0 },
    { name: 'Docker', category: 'devops', count: 4, share: 1.0, required_count: 4, preferred_count: 0 },
    { name: 'Python', category: 'language', count: 4, share: 1.0, required_count: 4, preferred_count: 0 },
    { name: 'MLflow', category: 'devops', count: 3, share: 0.75, required_count: 3, preferred_count: 0 },
    { name: 'Prometheus', category: 'devops', count: 3, share: 0.75, required_count: 2, preferred_count: 1 },
  ],
  'ML Engineer': [
    { name: 'PyTorch', category: 'ml_framework', count: 4, share: 1.0, required_count: 4, preferred_count: 0 },
    { name: 'Python', category: 'language', count: 4, share: 1.0, required_count: 4, preferred_count: 0 },
    { name: 'Ray', category: 'framework', count: 3, share: 0.75, required_count: 2, preferred_count: 1 },
    { name: 'CUDA', category: 'other', count: 3, share: 0.75, required_count: 3, preferred_count: 0 },
  ],
  'Data Scientist': [
    { name: 'Python', category: 'language', count: 3, share: 1.0, required_count: 3, preferred_count: 0 },
    { name: 'SQL', category: 'database', count: 3, share: 1.0, required_count: 3, preferred_count: 0 },
    { name: 'Pandas', category: 'framework', count: 3, share: 1.0, required_count: 3, preferred_count: 0 },
  ],
};

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'analytics' | 'explorer'>('explorer');
  const [selectedRole, setSelectedRole] = useState('AI Engineer');
  const [freshness, setFreshness] = useState<DataFreshness>({
    total_jobs: 8,
    active_jobs: 7,
    analyzed_jobs: 7,
    latest_job_crawled_at: new Date().toISOString(),
  });
  const [skills, setSkills] = useState<SkillStat[]>(SAMPLE_SKILLS['AI Engineer']);
  const [jobs, setJobs] = useState<JobItem[]>(MULTI_SOURCE_JOBS);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedJobModal, setSelectedJobModal] = useState<JobItem | null>(null);
  const [isLiveApi, setIsLiveApi] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        const freshRes = await fetch('http://localhost:8000/system/data-freshness');
        if (freshRes.ok) {
          const freshData = await freshRes.json();
          setFreshness(freshData);
          setIsLiveApi(true);
        }
        const skillsRes = await fetch(`http://localhost:8000/roles/${encodeURIComponent(selectedRole)}/skills`);
        if (skillsRes.ok) {
          const skillsData = await skillsRes.json();
          if (skillsData.skills && skillsData.skills.length > 0) {
            setSkills(skillsData.skills);
          }
        }

        const jobsRes = await fetch('http://localhost:8000/api/v1/jobs');
        if (jobsRes.ok) {
          const jobsData = await jobsRes.json();
          if (jobsData.items && jobsData.items.length > 0) {
            // Map live items
            const mapped = jobsData.items.map((it: any, idx: number) => ({
              ...it,
              posted_time_ago: it.posted_at ? 'Recently posted' : '1 day ago',
              ingestion_stage: 'Live Engine Ingested',
            }));
            setJobs(mapped);
          }
        }
      } catch (e) {
        setIsLiveApi(false);
        setSkills(SAMPLE_SKILLS[selectedRole] || []);
        setJobs(MULTI_SOURCE_JOBS);
      }
    }
    fetchData();
  }, [selectedRole]);

  const filteredJobs = jobs.filter(
    (j) =>
      j.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      j.company_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-8 bg-slate-50 min-h-screen text-slate-900 font-sans p-2 sm:p-4">
      {/* Top Banner - Clean Slate Light Style */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
              AI Job Intelligence Platform
            </span>
            <span className="text-xs text-slate-500 font-medium">PostgreSQL 18 • Redis Worker Queue</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight mt-2">
            Tech Market & Skill Intelligence
          </h1>
          <p className="text-slate-600 mt-1.5 text-sm max-w-3xl leading-relaxed">
            Continuous ingestion from Greenhouse, Lever, Workday, TopCV, Foorilla & Jobright with 0-Token pre-filtering and 2-stage deep crawling.
          </p>
        </div>

        {/* Tab Navigation Controls */}
        <div className="flex items-center space-x-2 bg-slate-100 p-1.5 rounded-2xl border border-slate-200">
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'analytics'
                ? 'bg-white text-indigo-700 shadow-sm border border-slate-200'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Market Analytics
          </button>
          <button
            onClick={() => setActiveTab('explorer')}
            className={`px-5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
              activeTab === 'explorer'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Briefcase className="w-4 h-4" />
            <span>Job Explorer ({jobs.length})</span>
          </button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs uppercase font-bold tracking-wider">Total Jobs Ingested</span>
            <Database className="w-5 h-5 text-indigo-600" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900">{freshness.total_jobs}</div>
          <div className="text-xs text-emerald-600 font-semibold flex items-center space-x-1">
            <CheckCircle className="w-3.5 h-3.5" />
            <span>100% SHA256 Deduplicated</span>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs uppercase font-bold tracking-wider">Active Postings</span>
            <Activity className="w-5 h-5 text-emerald-600" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900">{freshness.active_jobs}</div>
          <div className="text-xs text-slate-500 font-medium">6 ATS & Aggregators Connected</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs uppercase font-bold tracking-wider">AI Skill Analyzed</span>
            <Cpu className="w-5 h-5 text-purple-600" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900">{freshness.analyzed_jobs}</div>
          <div className="text-xs text-purple-700 font-medium">9Router + Gemini 3.6 Flash</div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs uppercase font-bold tracking-wider">API Status</span>
            <Layers className="w-5 h-5 text-cyan-600" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900">{isLiveApi ? 'Live API' : 'Seeded'}</div>
          <div className="text-xs text-slate-500 font-medium">
            {isLiveApi ? 'FastAPI localhost:8000' : 'Backend Ready (port 8000)'}
          </div>
        </div>
      </div>

      {/* TAB 1: MARKET ANALYTICS */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-200 pb-4">
            <h2 className="text-2xl font-black text-slate-900">Skill Demands by Role</h2>
            <div className="flex flex-wrap gap-2">
              {ROLES.map((role) => (
                <button
                  key={role}
                  onClick={() => setSelectedRole(role)}
                  className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                    selectedRole === role
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                      : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200'
                  }`}
                >
                  {role}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-200 flex justify-between items-center bg-slate-50/50">
              <div>
                <h3 className="text-lg font-bold text-slate-900">{selectedRole} — Top Required Technologies</h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Aggregated skill frequencies and required vs preferred split from real job descriptions.
                </p>
              </div>
              <span className="text-xs font-mono bg-indigo-50 text-indigo-700 px-3 py-1.5 rounded-lg border border-indigo-200 font-bold">
                {skills.length} Skills Extracted
              </span>
            </div>

            <div className="divide-y divide-slate-100">
              {skills.map((skill, idx) => (
                <div
                  key={skill.name}
                  className="p-5 hover:bg-slate-50 transition flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="flex items-center space-x-4 min-w-[200px]">
                    <span className="text-xs font-mono text-slate-400 font-bold w-5">#{idx + 1}</span>
                    <div>
                      <span className="font-bold text-slate-900 text-base">{skill.name}</span>
                      <span className="ml-2.5 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-600 border border-slate-200">
                        {skill.category}
                      </span>
                    </div>
                  </div>

                  <div className="flex-1 max-w-md w-full space-y-1">
                    <div className="flex justify-between text-xs font-semibold text-slate-600">
                      <span>Market Share</span>
                      <span className="text-indigo-600 font-extrabold">{Math.round(skill.share * 100)}%</span>
                    </div>
                    <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-500 to-teal-400 rounded-full transition-all duration-500"
                        style={{ width: `${Math.round(skill.share * 100)}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3 text-xs font-semibold">
                    <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-lg">
                      {skill.required_count} Required
                    </span>
                    {skill.preferred_count > 0 && (
                      <span className="bg-amber-50 text-amber-700 border border-amber-200 px-2.5 py-1 rounded-lg">
                        {skill.preferred_count} Preferred
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: JOB EXPLORER (LIGHT SLATE HIGH-CONTRAST DESIGN + POSTED TIME BADGES) */}
      {activeTab === 'explorer' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-200 pb-4">
            <div>
              <h2 className="text-2xl font-black text-slate-900">Job Explorer & Live Ingestion Feed</h2>
              <p className="text-xs text-slate-500 mt-1">
                Explore normalized job postings with exact posted timestamps, extracted skills, and official apply links.
              </p>
            </div>

            {/* Search Filter Box */}
            <div className="relative w-full sm:w-80">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="text"
                placeholder="Search job title or company..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-white border border-slate-300 rounded-xl pl-10 pr-4 py-2 text-sm text-slate-900 focus:outline-none focus:border-indigo-600 shadow-sm"
              />
            </div>
          </div>

          {/* Job List Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {filteredJobs.map((job) => (
              <div
                key={job.id}
                className="bg-white p-6 rounded-3xl border border-slate-200 hover:border-indigo-300 hover:shadow-md transition flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex justify-between items-center gap-2">
                    <span className="px-2.5 py-1 rounded-lg text-[10px] font-extrabold uppercase tracking-wider bg-indigo-50 text-indigo-700 border border-indigo-200">
                      {job.role_family} ({job.seniority})
                    </span>

                    <div className="flex items-center space-x-2">
                      {/* POSTED TIME AGO BADGE */}
                      <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold bg-slate-100 text-slate-600 border border-slate-200 flex items-center space-x-1">
                        <Clock className="w-3 h-3 text-slate-500" />
                        <span>{job.posted_time_ago || 'Recently posted'}</span>
                      </span>

                      {job.is_relevant ? (
                        <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-700 border border-emerald-200">
                          Pass (AI Tech)
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider bg-amber-50 text-amber-700 border border-amber-200 flex items-center space-x-1">
                          <Lock className="w-3 h-3" />
                          <span>Paywall / Audit</span>
                        </span>
                      )}
                    </div>
                  </div>

                  <h3 className="text-xl font-bold text-slate-900 leading-snug hover:text-indigo-600 transition">
                    {job.title}
                  </h3>

                  <div className="flex flex-wrap items-center gap-y-1.5 gap-x-4 text-xs text-slate-600 font-medium">
                    <span className="flex items-center space-x-1.5 text-slate-900 font-bold">
                      <Building2 className="w-4 h-4 text-indigo-600" />
                      <span>{job.company_name}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <MapPin className="w-4 h-4 text-slate-400" />
                      <span>{job.location}</span>
                    </span>
                  </div>

                  {job.salary_range && (
                    <div className="flex items-center space-x-1.5 text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-lg border border-emerald-200 w-fit">
                      <DollarSign className="w-3.5 h-3.5" />
                      <span>{job.salary_range}</span>
                    </div>
                  )}

                  <p className="text-xs text-slate-600 line-clamp-3 leading-relaxed font-sans">
                    {job.description_text}
                  </p>

                  {/* Skills Badges */}
                  {job.skills && job.skills.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-2">
                      {job.skills.map((s) => (
                        <span
                          key={s.name}
                          className="px-2.5 py-1 rounded-lg text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-200"
                        >
                          {s.name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Footer Action Buttons */}
                <div className="pt-4 border-t border-slate-100 flex items-center justify-between gap-2">
                  <button
                    onClick={() => setSelectedJobModal(job)}
                    className="text-xs font-bold text-indigo-600 hover:text-indigo-800 transition flex items-center space-x-1"
                  >
                    <BookOpen className="w-3.5 h-3.5" />
                    <span>View Formatted Detail</span>
                  </button>

                  <a
                    href={job.canonical_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm transition"
                  >
                    <span>Apply on Official Portal</span>
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* RICH FORMATTED STAGE-2 DETAIL PANORAMA MODAL (CLEAN LIGHT THEME) */}
      {selectedJobModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white w-full max-w-4xl max-h-[92vh] rounded-3xl border border-slate-200 p-6 sm:p-8 overflow-y-auto space-y-6 text-slate-900 shadow-2xl">
            {/* Modal Header */}
            <div className="flex justify-between items-start border-b border-slate-200 pb-5">
              <div className="space-y-2">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="px-3 py-1 rounded-lg text-xs font-bold uppercase tracking-wider bg-indigo-50 text-indigo-700 border border-indigo-200">
                    {selectedJobModal.role_family} ({selectedJobModal.seniority})
                  </span>

                  <span className="px-3 py-1 rounded-lg text-xs font-bold bg-slate-100 text-slate-700 border border-slate-200 flex items-center space-x-1">
                    <Clock className="w-3.5 h-3.5 text-slate-500" />
                    <span>Posted {selectedJobModal.posted_time_ago || 'Recently'}</span>
                  </span>

                  {selectedJobModal.ingestion_stage && (
                    <span className="px-3 py-1 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center space-x-1">
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>{selectedJobModal.ingestion_stage}</span>
                    </span>
                  )}
                </div>

                <h2 className="text-2xl sm:text-3xl font-black text-slate-900 leading-snug tracking-tight">
                  {selectedJobModal.title}
                </h2>

                <div className="flex flex-wrap items-center gap-4 text-xs text-slate-600 font-medium">
                  <span className="flex items-center space-x-1 text-slate-900 font-bold">
                    <Building2 className="w-4 h-4 text-indigo-600" />
                    <span>{selectedJobModal.company_name}</span>
                  </span>
                  <span className="flex items-center space-x-1 text-slate-500">
                    <MapPin className="w-4 h-4 text-slate-400" />
                    <span>{selectedJobModal.location}</span>
                  </span>
                </div>
              </div>

              <button
                onClick={() => setSelectedJobModal(null)}
                className="p-2 rounded-xl text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Salary Highlight Callout Box */}
            {selectedJobModal.salary_range && (
              <div className="bg-gradient-to-r from-emerald-50 via-teal-50 to-indigo-50 p-5 rounded-2xl border border-emerald-200 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-3 rounded-xl bg-white border border-emerald-200 text-emerald-700 shadow-sm">
                    <DollarSign className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs uppercase font-extrabold tracking-wider text-emerald-800">Expected Compensation</span>
                    <h4 className="text-xl font-black text-slate-900">{selectedJobModal.salary_range}</h4>
                  </div>
                </div>
                <a
                  href={selectedJobModal.canonical_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hidden sm:inline-flex items-center space-x-1.5 px-4 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm transition"
                >
                  <span>Apply Now</span>
                  <ArrowUpRight className="w-4 h-4" />
                </a>
              </div>
            )}

            {/* Extracted Required Tech Stack with Evidence Spans */}
            <div className="space-y-3 bg-slate-50 p-5 rounded-2xl border border-slate-200">
              <h4 className="text-xs uppercase tracking-wider text-slate-500 font-extrabold flex items-center space-x-2">
                <Award className="w-4 h-4 text-indigo-600" />
                <span>Extracted Tech Stack & LLM Evidence Spans</span>
              </h4>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {selectedJobModal.skills.map((s) => (
                  <div
                    key={s.name}
                    className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between space-y-1"
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-slate-900 text-sm">{s.name}</span>
                      <span
                        className={`px-2.5 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                          s.requirement_type === 'required'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : 'bg-amber-50 text-amber-700 border border-amber-200'
                        }`}
                      >
                        {s.requirement_type || 'required'}
                      </span>
                    </div>
                    {s.evidence_text && (
                      <p className="text-[11px] text-slate-500 italic line-clamp-1">"{s.evidence_text}"</p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Structured Multi-Section Description Body */}
            {selectedJobModal.sections ? (
              <div className="space-y-6">
                {/* Overview Section */}
                {selectedJobModal.sections.overview && (
                  <div className="space-y-2">
                    <h3 className="text-sm uppercase tracking-wider font-extrabold text-indigo-700 flex items-center space-x-2">
                      <Globe className="w-4 h-4" />
                      <span>Company Overview & Mission</span>
                    </h3>
                    <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-4.5 rounded-2xl border border-slate-200">
                      {selectedJobModal.sections.overview}
                    </p>
                  </div>
                )}

                {/* Responsibilities Section */}
                {selectedJobModal.sections.responsibilities && (
                  <div className="space-y-2">
                    <h3 className="text-sm uppercase tracking-wider font-extrabold text-emerald-700 flex items-center space-x-2">
                      <ShieldCheck className="w-4 h-4" />
                      <span>What You'll Do & Key Responsibilities</span>
                    </h3>
                    <ul className="space-y-2 text-xs text-slate-700 bg-slate-50 p-4.5 rounded-2xl border border-slate-200">
                      {selectedJobModal.sections.responsibilities.map((r, idx) => (
                        <li key={idx} className="flex items-start space-x-2.5">
                          <span className="text-emerald-600 font-bold text-sm leading-none">•</span>
                          <span className="leading-relaxed">{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Requirements Section */}
                {selectedJobModal.sections.requirements && (
                  <div className="space-y-2">
                    <h3 className="text-sm uppercase tracking-wider font-extrabold text-purple-700 flex items-center space-x-2">
                      <CheckCircle className="w-4 h-4" />
                      <span>Qualifications & Success Requirements</span>
                    </h3>
                    <ul className="space-y-2 text-xs text-slate-700 bg-slate-50 p-4.5 rounded-2xl border border-slate-200">
                      {selectedJobModal.sections.requirements.map((req, idx) => (
                        <li key={idx} className="flex items-start space-x-2.5">
                          <span className="text-purple-600 font-bold text-sm leading-none">•</span>
                          <span className="leading-relaxed">{req}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Regional Salary Ranges */}
                {selectedJobModal.sections.salary_info && (
                  <div className="space-y-2">
                    <h3 className="text-sm uppercase tracking-wider font-extrabold text-amber-700 flex items-center space-x-2">
                      <DollarSign className="w-4 h-4" />
                      <span>Regional Salary Ranges</span>
                    </h3>
                    <div className="space-y-1.5 text-xs text-slate-700 bg-slate-50 p-4.5 rounded-2xl border border-slate-200 font-mono">
                      {selectedJobModal.sections.salary_info.map((sal, idx) => (
                        <div key={idx} className="flex items-center space-x-2">
                          <span className="text-amber-600 font-bold">•</span>
                          <span>{sal}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              /* Fallback for un-parsed text */
              <div className="space-y-2">
                <h4 className="text-xs uppercase tracking-wider text-slate-500 font-bold">Complete Job Description Text</h4>
                <div className="text-xs text-slate-800 bg-slate-50 p-5 rounded-2xl border border-slate-200 leading-relaxed font-sans whitespace-pre-wrap max-h-96 overflow-y-auto">
                  {selectedJobModal.description_text}
                </div>
              </div>
            )}

            {/* Modal Footer Actions */}
            <div className="pt-4 border-t border-slate-200 flex justify-between items-center">
              <button
                onClick={() => setSelectedJobModal(null)}
                className="px-5 py-2.5 rounded-xl text-xs font-bold text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition"
              >
                Close Panel
              </button>
              <a
                href={selectedJobModal.canonical_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl text-xs font-black bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-600/20 transition"
              >
                <span>Apply on Official Portal ({selectedJobModal.company_name})</span>
                <ArrowUpRight className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
