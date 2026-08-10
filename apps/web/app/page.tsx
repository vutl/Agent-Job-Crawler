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
  id: number;
  title: string;
  company_name: string;
  company_domain?: string;
  canonical_url: string;
  location: string;
  description_text: string;
  posted_at: string | null;
  role_family: string;
  seniority: string;
  is_relevant: boolean;
  relevance_reason: string | null;
  skills: JobSkill[];
}

const ROLES = ['AI Engineer', 'ML Engineer', 'MLOps Engineer', 'Data Scientist'];

const THUMBTACK_FULL_DESCRIPTION = `Software Engineer, AI/ML Infrastructure (US-Based)
Location: Remote, United States
Employment Type: Full time | Department: Engineering

Overview & Application
Thumbtack helps millions of people confidently care for their homes. Thumbtack is the one app you need to take care of and improve your home — from personalized guidance to AI tools and a best-in-class hiring experience. Every day in every county of the U.S., people turn to Thumbtack to complete urgent repairs, seasonal maintenance and bigger improvements. We help homeowners know which projects to do, when to do them and who to hire from our growing community of 300,000 local service businesses. If making an impact inspires you, join us. Imagine what we’ll build together.

About the Machine Learning Infrastructure Team
At Thumbtack, our challenges span a wide range of areas, including search, recommendations, matchmaking, pricing, safety, content generation, fraud detection, and more. The ML Infrastructure team is responsible for centralizing, standardizing and evolving AI/ML infrastructure that enables these experiences. We empower product engineering teams by providing scalable, high-performance systems that drive AI innovation at scale. To read more about some of the engineering challenges at Thumbtack, visit our engineering blog.

The Challenge
As a Software Engineer on the ML Infrastructure team, you will work closely with product and platform engineering teams to build and evolve core AI platform capabilities. You will help design and improve systems that allow teams to develop, run, and scale GenAI-powered applications in production. Your work will directly support AI-driven experiences used by millions of customers and pros across the Thumbtack ecosystem.

What You’ll Do
- Build and evolve core AI platform capabilities that enable teams to develop, run, and scale GenAI-powered applications across Thumbtack.
- Contribute to the design, development, and deployment of scalable tools and infrastructure to support the efforts of our applied scientists, including traditional ML model training and serving systems, feature and data workflows, CI/CD, orchestration, deployment, and evaluation tooling.
- Work hands on across the stack, from backend services and execution infrastructure to integrations with AI models and tooling.
- Partner with senior engineers to evaluate next-generation AI infrastructure frameworks and tools that help product teams harness advances in AI.
- Drive projects to completion with a strong focus on business impact and measurable outcomes.
- Solve complex technical problems and stay up to date with advances in this rapidly evolving space.

In Order to Be Successful, You Must Bring
- 1 to 3 years of professional software engineering experience.
- Strong fundamentals in data structures, algorithms, and software design.
- Proficiency in at least one major programming language, and the ability to work across multiple languages. Our primary stack includes Go and Python.
- Experience working with relational or NoSQL databases such as Postgres or DynamoDB.
- Demonstrated ability to use AI coding tools in day-to-day workflows and validate, critique, and refine AI-generated output.
- Comfort operating in a fast-paced environment with a certain level of ambiguity, especially when learning and picking up new technologies when projects require it.
- You operate with a bias to action, quickly learning what is needed and taking decisive steps to move work forward in ambiguous, fast-paced environments.

Expected Salary Ranges
- San Francisco / Bay Area, San Jose, NYC, Seattle metros: $145,400 - $188,100 / yr
- Austin TX, Washington DC, CA, MA, NJ, WA states: $130,900 - $169,400 / yr
- All other US locations: $123,300 - $159,500 / yr

Company Overview & Sponsorship
Thumbtack was founded in 2008, headquartered in San Francisco, CA (1,001-5,000 employees). Has a track record of offering H1B sponsorships (16 in 2026, 35 in 2025, 48 in 2024). Equal Opportunity Workplace.`;

const SAMPLE_JOBS: JobItem[] = [
  {
    id: 1,
    title: 'Software Engineer, AI/ML Infrastructure (US-Based)',
    company_name: 'Thumbtack',
    company_domain: 'thumbtack.com',
    canonical_url: 'https://jobs.ashbyhq.com/thumbtack/3efb1a7b-cfaf-475a-86a9-abff37581b4b/application',
    location: 'United States (Remote)',
    description_text: THUMBTACK_FULL_DESCRIPTION,
    posted_at: new Date().toISOString(),
    role_family: 'AI Engineer',
    seniority: 'Entry Level',
    is_relevant: true,
    relevance_reason: 'Core AI Infrastructure role matching technical criteria',
    skills: [
      { name: 'Python', requirement_type: 'required' },
      { name: 'Go', requirement_type: 'required' },
      { name: 'PyTorch', requirement_type: 'required' },
      { name: 'Postgres', requirement_type: 'required' },
      { name: 'DynamoDB', requirement_type: 'preferred' },
    ],
  },
  {
    id: 2,
    title: 'Artificial Intelligence Intern',
    company_name: 'Muro AI',
    company_domain: 'muro.ai',
    canonical_url: 'https://www.linkedin.com/jobs/view/4446448878',
    location: 'San Francisco Bay Area (Onsite)',
    description_text:
      'Muro AI builds AI agents for general contractor companies to automate pre-construction activities and streamline complex workflows. As an Artificial Intelligence Intern, you will support the development of AI agents and collaborate with engineers and data scientists to improve pre-construction workflows.\n\nResponsibilities:\n- Support the development and improvement of AI agents\n- Help design and implement models\n- Write and test code in Python\n- Analyze data & evaluate model performance\n- Document findings and refine algorithms\n\nSkills & Requirements:\n- Computer Science foundation, algorithms, data structures\n- Data Science & Machine Learning exposure\n- Python programming & Git version control\n- Interest in applying AI to construction & architecture',
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
  },
  {
    id: 3,
    title: 'Senior AI Engineer',
    company_name: 'Cloudflare',
    company_domain: 'cloudflare.com',
    canonical_url: 'https://boards.greenhouse.io/cloudflare/jobs/40101',
    location: 'San Francisco, CA',
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
  },
  {
    id: 4,
    title: 'AI R&D Co-op (Account Locked)',
    company_name: 'Foorilla Partner',
    company_domain: 'foorilla.com',
    canonical_url: 'https://foorilla.com/account/login/?next=/hiring/jobs/1029',
    location: 'Remote (US)',
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
    { name: 'Python', category: 'language', count: 4, share: 1.0, required_count: 4, preferred_count: 0 },
    { name: 'PyTorch', category: 'ml_framework', count: 4, share: 1.0, required_count: 3, preferred_count: 1 },
    { name: 'LangChain', category: 'framework', count: 3, share: 0.75, required_count: 2, preferred_count: 1 },
    { name: 'FastAPI', category: 'framework', count: 3, share: 0.75, required_count: 2, preferred_count: 1 },
    { name: 'Kubernetes', category: 'devops', count: 3, share: 0.75, required_count: 3, preferred_count: 0 },
    { name: 'Docker', category: 'devops', count: 3, share: 0.75, required_count: 3, preferred_count: 0 },
    { name: 'AWS', category: 'cloud', count: 2, share: 0.5, required_count: 2, preferred_count: 0 },
    { name: 'PostgreSQL / pgvector', category: 'database', count: 2, share: 0.5, required_count: 2, preferred_count: 0 },
  ],
  'MLOps Engineer': [
    { name: 'Kubernetes', category: 'devops', count: 3, share: 1.0, required_count: 3, preferred_count: 0 },
    { name: 'Docker', category: 'devops', count: 3, share: 1.0, required_count: 3, preferred_count: 0 },
    { name: 'Python', category: 'language', count: 3, share: 1.0, required_count: 3, preferred_count: 0 },
    { name: 'Terraform', category: 'devops', count: 2, share: 0.66, required_count: 2, preferred_count: 0 },
    { name: 'Prometheus', category: 'devops', count: 2, share: 0.66, required_count: 1, preferred_count: 1 },
  ],
  'ML Engineer': [
    { name: 'PyTorch', category: 'ml_framework', count: 3, share: 1.0, required_count: 3, preferred_count: 0 },
    { name: 'Python', category: 'language', count: 3, share: 1.0, required_count: 3, preferred_count: 0 },
    { name: 'Ray', category: 'framework', count: 2, share: 0.66, required_count: 1, preferred_count: 1 },
    { name: 'CUDA', category: 'other', count: 2, share: 0.66, required_count: 2, preferred_count: 0 },
  ],
  'Data Scientist': [
    { name: 'Python', category: 'language', count: 2, share: 1.0, required_count: 2, preferred_count: 0 },
    { name: 'SQL', category: 'database', count: 2, share: 1.0, required_count: 2, preferred_count: 0 },
    { name: 'Pandas', category: 'framework', count: 2, share: 1.0, required_count: 2, preferred_count: 0 },
  ],
};

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'analytics' | 'explorer'>('analytics');
  const [selectedRole, setSelectedRole] = useState('AI Engineer');
  const [freshness, setFreshness] = useState<DataFreshness>({
    total_jobs: 4,
    active_jobs: 4,
    analyzed_jobs: 4,
    latest_job_crawled_at: new Date().toISOString(),
  });
  const [skills, setSkills] = useState<SkillStat[]>(SAMPLE_SKILLS['AI Engineer']);
  const [jobs, setJobs] = useState<JobItem[]>(SAMPLE_JOBS);
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
            setJobs(jobsData.items);
          }
        }
      } catch (e) {
        setIsLiveApi(false);
        setSkills(SAMPLE_SKILLS[selectedRole] || []);
        setJobs(SAMPLE_JOBS);
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
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-gradient-to-r from-indigo-900/30 via-slate-900 to-emerald-900/20 p-6 rounded-2xl border border-indigo-500/20 shadow-xl">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            AI Job Market Intelligence
          </h1>
          <p className="text-gray-400 mt-1 text-sm">
            Continuous ingestion from Greenhouse, Lever, Workday, TopCV, Foorilla & Jobright with 0-Token pre-filtering.
          </p>
        </div>

        {/* Tab Navigation Controls */}
        <div className="flex items-center space-x-2 bg-gray-900/80 p-1.5 rounded-xl border border-gray-800">
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'analytics'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Market Analytics
          </button>
          <button
            onClick={() => setActiveTab('explorer')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center space-x-1.5 ${
              activeTab === 'explorer'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <Briefcase className="w-3.5 h-3.5" />
            <span>Job Explorer ({jobs.length})</span>
          </button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 rounded-xl border border-gray-800 space-y-2">
          <div className="flex items-center justify-between text-gray-400">
            <span className="text-xs uppercase font-medium tracking-wider">Total Jobs Ingested</span>
            <Database className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="text-3xl font-bold text-white">{freshness.total_jobs}</div>
          <div className="text-xs text-emerald-400 flex items-center space-x-1">
            <CheckCircle className="w-3 h-3" />
            <span>100% Deduplicated</span>
          </div>
        </div>

        <div className="glass-card p-5 rounded-xl border border-gray-800 space-y-2">
          <div className="flex items-center justify-between text-gray-400">
            <span className="text-xs uppercase font-medium tracking-wider">Active Postings</span>
            <Activity className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="text-3xl font-bold text-white">{freshness.active_jobs}</div>
          <div className="text-xs text-gray-400">6 ATS & Aggregators Connected</div>
        </div>

        <div className="glass-card p-5 rounded-xl border border-gray-800 space-y-2">
          <div className="flex items-center justify-between text-gray-400">
            <span className="text-xs uppercase font-medium tracking-wider">AI Skill Analyzed</span>
            <Cpu className="w-5 h-5 text-purple-400" />
          </div>
          <div className="text-3xl font-bold text-white">{freshness.analyzed_jobs}</div>
          <div className="text-xs text-purple-300">9Router + Gemini 3.6 Flash</div>
        </div>

        <div className="glass-card p-5 rounded-xl border border-gray-800 space-y-2">
          <div className="flex items-center justify-between text-gray-400">
            <span className="text-xs uppercase font-medium tracking-wider">API Status</span>
            <Layers className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="text-3xl font-bold text-white">{isLiveApi ? 'Live API' : 'Seeded'}</div>
          <div className="text-xs text-gray-400">
            {isLiveApi ? 'FastAPI localhost:8000' : 'Backend Ready (port 8000)'}
          </div>
        </div>
      </div>

      {/* TAB 1: MARKET ANALYTICS */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-gray-800 pb-4">
            <h2 className="text-xl font-bold text-white">Skill Demands by Role</h2>
            <div className="flex flex-wrap gap-2">
              {ROLES.map((role) => (
                <button
                  key={role}
                  onClick={() => setSelectedRole(role)}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                    selectedRole === role
                      ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                      : 'bg-gray-800/60 text-gray-400 hover:text-white hover:bg-gray-800'
                  }`}
                >
                  {role}
                </button>
              ))}
            </div>
          </div>

          <div className="glass-card rounded-2xl border border-gray-800 overflow-hidden">
            <div className="p-6 border-b border-gray-800 flex justify-between items-center">
              <div>
                <h3 className="text-lg font-bold text-white">{selectedRole} — Top Required Technologies</h3>
                <p className="text-xs text-gray-400 mt-0.5">
                  Aggregated skill frequencies and required vs preferred split from real job descriptions.
                </p>
              </div>
              <span className="text-xs font-mono bg-gray-800 px-3 py-1.5 rounded-lg text-gray-300 border border-gray-700">
                {skills.length} Skills Extracted
              </span>
            </div>

            <div className="divide-y divide-gray-800/60">
              {skills.map((skill, idx) => (
                <div
                  key={skill.name}
                  className="p-4 sm:p-5 hover:bg-gray-800/30 transition flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="flex items-center space-x-4 min-w-[200px]">
                    <span className="text-xs font-mono text-gray-500 w-5">#{idx + 1}</span>
                    <div>
                      <span className="font-semibold text-white text-base">{skill.name}</span>
                      <span className="ml-2.5 px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-gray-800 text-gray-400 border border-gray-700">
                        {skill.category}
                      </span>
                    </div>
                  </div>

                  <div className="flex-1 max-w-md w-full space-y-1">
                    <div className="flex justify-between text-xs font-medium text-gray-400">
                      <span>Market Share</span>
                      <span className="text-indigo-400 font-bold">{Math.round(skill.share * 100)}%</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-gray-800 overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 rounded-full transition-all duration-500"
                        style={{ width: `${Math.round(skill.share * 100)}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4 text-xs font-medium text-gray-400">
                    <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded-lg">
                      {skill.required_count} Required
                    </span>
                    {skill.preferred_count > 0 && (
                      <span className="bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2.5 py-1 rounded-lg">
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

      {/* TAB 2: JOB EXPLORER (CHI TIẾT TỪNG JOB + OUTBOUND APPLY LINK) */}
      {activeTab === 'explorer' && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-gray-800 pb-4">
            <div>
              <h2 className="text-xl font-bold text-white">Job Explorer & Ingestion Feed</h2>
              <p className="text-xs text-gray-400 mt-1">
                Explore normalized job postings, full multi-section JD descriptions, extracted skills, and official apply links.
              </p>
            </div>

            {/* Search Filter Box */}
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
              <input
                type="text"
                placeholder="Search job title or company..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-gray-900 border border-gray-800 rounded-xl pl-9 pr-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          {/* Job List Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredJobs.map((job) => (
              <div
                key={job.id}
                className="glass-card p-6 rounded-2xl border border-gray-800 hover:border-indigo-500/40 transition flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex justify-between items-start gap-2">
                    <span className="px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      {job.role_family} ({job.seniority})
                    </span>

                    {job.is_relevant ? (
                      <span className="px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        Pass (AI Tech)
                      </span>
                    ) : (
                      <span className="px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center space-x-1">
                        <Lock className="w-3 h-3" />
                        <span>Paywall / Audit</span>
                      </span>
                    )}
                  </div>

                  <h3 className="text-lg font-bold text-white leading-snug hover:text-indigo-300 transition">
                    {job.title}
                  </h3>

                  <div className="flex flex-wrap items-center gap-y-1 gap-x-4 text-xs text-gray-400">
                    <span className="flex items-center space-x-1 text-gray-300 font-semibold">
                      <Building2 className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{job.company_name}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <MapPin className="w-3.5 h-3.5 text-gray-500" />
                      <span>{job.location}</span>
                    </span>
                  </div>

                  <p className="text-xs text-gray-400 line-clamp-3 leading-relaxed">
                    {job.description_text}
                  </p>

                  {/* Skills Badges */}
                  {job.skills && job.skills.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-2">
                      {job.skills.map((s) => (
                        <span
                          key={s.name}
                          className="px-2 py-0.5 rounded text-[11px] font-medium bg-gray-800 text-indigo-300 border border-gray-700"
                        >
                          {s.name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Footer Action Buttons */}
                <div className="pt-4 border-t border-gray-800/80 flex items-center justify-between gap-2">
                  <button
                    onClick={() => setSelectedJobModal(job)}
                    className="text-xs font-semibold text-gray-400 hover:text-white transition underline underline-offset-4"
                  >
                    View Full Description ({job.description_text.length} chars)
                  </button>

                  <a
                    href={job.canonical_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20 transition"
                  >
                    <span>Apply on Company Site</span>
                    <ArrowUpRight className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* FULL DESCRIPTION DETAIL MODAL POPUP */}
      {selectedJobModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="glass-card w-full max-w-3xl max-h-[90vh] rounded-2xl border border-gray-700 p-6 sm:p-8 overflow-y-auto space-y-6 bg-slate-900 text-white shadow-2xl">
            <div className="flex justify-between items-start border-b border-gray-800 pb-4">
              <div>
                <span className="px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  {selectedJobModal.role_family} ({selectedJobModal.seniority})
                </span>
                <h2 className="text-2xl font-bold text-white mt-2 leading-snug">{selectedJobModal.title}</h2>
                <p className="text-xs text-gray-400 mt-1">
                  {selectedJobModal.company_name} • {selectedJobModal.location}
                </p>
              </div>
              <button
                onClick={() => setSelectedJobModal(null)}
                className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-3">
              <h4 className="text-xs uppercase tracking-wider text-gray-400 font-bold">Extracted Required Tech Stack</h4>
              <div className="flex flex-wrap gap-2">
                {selectedJobModal.skills.map((s) => (
                  <span
                    key={s.name}
                    className="px-3 py-1 rounded-lg text-xs font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20"
                  >
                    {s.name} ({s.requirement_type || 'required'})
                  </span>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-xs uppercase tracking-wider text-gray-400 font-bold">Relevance & Filter Status</h4>
              <p className="text-xs text-gray-300 bg-gray-800/60 p-3.5 rounded-xl border border-gray-700">
                {selectedJobModal.relevance_reason || 'Passed AI technical evaluation pipeline.'}
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <h4 className="text-xs uppercase tracking-wider text-gray-400 font-bold">Complete Job Description Text (Full Un-truncated)</h4>
                <span className="text-[11px] font-mono text-gray-500">{selectedJobModal.description_text.length} characters</span>
              </div>
              <div className="text-xs text-gray-200 bg-gray-950 p-5 rounded-xl border border-gray-800 leading-relaxed font-sans whitespace-pre-wrap max-h-96 overflow-y-auto space-y-4">
                {selectedJobModal.description_text}
              </div>
            </div>

            <div className="pt-4 border-t border-gray-800 flex justify-between items-center">
              <button
                onClick={() => setSelectedJobModal(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-gray-400 hover:text-white hover:bg-gray-800 transition"
              >
                Close
              </button>
              <a
                href={selectedJobModal.canonical_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/30 transition"
              >
                <span>Apply on Official Portal</span>
                <ArrowUpRight className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
