'use client';

import React, { useState, useEffect, useMemo } from 'react';
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
  ShieldAlert,
  ChevronRight,
  Compass,
  BarChart3,
  Flame,
  Check,
  Tag,
  Eye,
  RefreshCw,
  Bot,
  HeartPulse,
  CreditCard,
  Lightbulb,
  Rocket,
  Zap,
  CheckCircle2,
  Target,
  Code2,
  Terminal,
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

interface DomainIndustryContext {
  summary: string;
  companies_hiring: string[];
  real_world_tasks: string[];
}

interface DomainInternExpectations {
  core_theories: string[];
  engineering_skills: string[];
  cost_latency_tradeoffs: string[];
}

interface DomainCapstoneBlueprint {
  project_name: string;
  value_prop: string;
  core_problem: string;
  system_architecture: string[];
  key_metrics_to_show: string[];
  standout_factor: string;
}

interface DomainIntelligenceItem {
  id: string;
  title: string;
  tagline: string;
  icon: string;
  badge: string;
  target_roles: string[];
  industry_context: DomainIndustryContext;
  intern_junior_expectations: DomainInternExpectations;
  capstone_blueprint: DomainCapstoneBlueprint;
}

interface JobItem {
  id: number | string;
  external_id?: string;
  title: string;
  company_name: string;
  company_domain?: string;
  canonical_url: string;
  location: string;
  salary_range?: string;
  description_text: string;
  posted_time_ago?: string;
  posted_at?: string | null;
  role_family: string;
  seniority: string;
  is_relevant: boolean;
  relevance_reason: string | null;
  status: string;
  skills: JobSkill[];
}

const ROLES = ['AI Engineer', 'ML Engineer', 'MLOps Engineer', 'Data Scientist'];

// Helper to extract valid Jobright 24-hex deep links
function getValidJobrightUrl(externalId?: string, canonicalUrl?: string, desc?: string): string | null {
  if (externalId && /^[a-f0-9]{24}$/i.test(externalId)) {
    return `https://jobright.ai/jobs/info/${externalId}#overview`;
  }
  if (canonicalUrl && canonicalUrl.includes('jobright.ai/jobs/info/')) {
    const match = canonicalUrl.match(/https:\/\/jobright\.ai\/jobs\/info\/([a-f0-9]{24})/i);
    if (match) return `https://jobright.ai/jobs/info/${match[1]}#overview`;
  }
  if (desc) {
    const match = desc.match(/https:\/\/jobright\.ai\/jobs\/info\/([a-f0-9]{24})/i);
    if (match) return `https://jobright.ai/jobs/info/${match[1]}#overview`;
  }
  return null;
}

// Helper to render Markdown Job Description into clean structured HTML
function MarkdownJDViewer({ content }: { content: string }) {
  if (!content) return <p className="text-slate-400 italic">No description available.</p>;

  // Split by double newlines into blocks
  const blocks = content.split(/\n\n+/);

  return (
    <div className="jd-markdown-content space-y-4">
      {blocks.map((block, idx) => {
        const trimmed = block.trim();
        if (!trimmed) return null;

        // Heading 3: ### Heading
        if (trimmed.startsWith('### ')) {
          const headingText = trimmed.replace(/^###\s+/, '');
          return (
            <h3 key={idx} className="flex items-center space-x-2">
              <span className="w-1.5 h-4 rounded-full bg-indigo-600 inline-block"></span>
              <span>{headingText}</span>
            </h3>
          );
        }

        // Bullet list
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
          const items = trimmed.split(/\n[-*]\s+/).filter(Boolean);
          return (
            <ul key={idx}>
              {items.map((item, itemIdx) => (
                <li key={itemIdx} className="flex items-start space-x-2">
                  <span className="text-indigo-500 mt-1 mr-1">•</span>
                  <span>{item.replace(/^[-*]\s+/, '')}</span>
                </li>
              ))}
            </ul>
          );
        }

        // Regular paragraph
        return <p key={idx}>{trimmed}</p>;
      })}
    </div>
  );
}

// Generate consistent avatar gradient by company name
function getCompanyAvatarGradient(name: string) {
  const gradients = [
    'from-indigo-600 to-violet-600',
    'from-emerald-600 to-teal-600',
    'from-cyan-600 to-blue-600',
    'from-rose-600 to-pink-600',
    'from-amber-600 to-orange-600',
    'from-fuchsia-600 to-purple-600',
  ];
  let hash = 0;
  for (let i = 0; i < (name || '').length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % gradients.length;
  return gradients[index];
}

// Get initials
function getInitials(name: string) {
  if (!name) return 'AI';
  const clean = name.replace(/Foorilla\s*\|\s*/i, '').replace(/TopCV\s*\|\s*/i, '');
  const parts = clean.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[1][0]).toUpperCase();
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<'explorer' | 'blueprints' | 'analytics' | 'vault'>('explorer');
  const [selectedRole, setSelectedRole] = useState('AI Engineer');
  const [skills, setSkills] = useState<SkillStat[]>([]);
  const [freshness, setFreshness] = useState<DataFreshness | null>(null);
  const [domainIntelligence, setDomainIntelligence] = useState<DomainIntelligenceItem[]>([]);
  const [selectedDomainId, setSelectedDomainId] = useState<string>('agentic-ai');
  
  // Public vs Locked jobs
  const [publicJobs, setPublicJobs] = useState<JobItem[]>([]);
  const [lockedJobs, setLockedJobs] = useState<JobItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSourceFilter, setSelectedSourceFilter] = useState('ALL');
  const [selectedRoleFilter, setSelectedRoleFilter] = useState('ALL');
  const [selectedSeniorityFilter, setSelectedSeniorityFilter] = useState('ALL');
  const [remoteOnly, setRemoteOnly] = useState(false);

  // Detail Modal
  const [selectedJobModal, setSelectedJobModal] = useState<JobItem | null>(null);

  // Fetch initial data
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [freshRes, pubRes, lockRes, domainRes] = await Promise.all([
          fetch('http://localhost:8000/system/data-freshness'),
          fetch('http://localhost:8000/api/v1/jobs?limit=1500&locked_only=false'),
          fetch('http://localhost:8000/api/v1/jobs?limit=1500&locked_only=true'),
          fetch('http://localhost:8000/api/v1/intelligence/domains'),
        ]);

        if (freshRes.ok) setFreshness(await freshRes.json());
        if (pubRes.ok) {
          const data = await pubRes.json();
          setPublicJobs(data.items || []);
        }
        if (lockRes.ok) {
          const data = await lockRes.json();
          setLockedJobs(data.items || []);
        }
        if (domainRes.ok) {
          const dData = await domainRes.json();
          setDomainIntelligence(dData.domains || []);
        }
      } catch (err) {
        console.error('Failed to load initial data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // Fetch role skills analytics
  useEffect(() => {
    async function loadRoleSkills() {
      try {
        const res = await fetch(`http://localhost:8000/roles/${encodeURIComponent(selectedRole)}/skills`);
        if (res.ok) {
          const data = await res.json();
          setSkills(data.skills || []);
        }
      } catch (err) {
        console.error('Failed to load skills:', err);
      }
    }
    loadRoleSkills();
  }, [selectedRole]);

  // Filtered Public Jobs
  const filteredPublicJobs = useMemo(() => {
    return publicJobs.filter((job) => {
      // Comprehensive Multi-Field Search
      if (searchQuery) {
        const q = searchQuery.toLowerCase().trim();
        const matchTitle = job.title.toLowerCase().includes(q);
        const matchCompany = job.company_name.toLowerCase().includes(q);
        const matchLoc = (job.location || '').toLowerCase().includes(q);
        const matchSkill = job.skills && job.skills.some((s) => s.name.toLowerCase().includes(q));
        const matchDesc = (job.description_text || '').toLowerCase().includes(q);
        if (!matchTitle && !matchCompany && !matchLoc && !matchSkill && !matchDesc) return false;
      }

      // Source Filter
      if (selectedSourceFilter !== 'ALL') {
        const url = job.canonical_url.toLowerCase();
        const cname = job.company_name.toLowerCase();
        if (selectedSourceFilter === 'DIRECT_ATS') {
          if (!url.includes('greenhouse') && !url.includes('lever') && !url.includes('workday') && !cname.includes('cloudflare') && !cname.includes('spotify') && !cname.includes('datarobot')) {
            return false;
          }
        } else if (selectedSourceFilter === 'FOORILLA') {
          if (!cname.includes('foorilla') && !url.includes('foorilla')) return false;
        } else if (selectedSourceFilter === 'JOBRIGHT') {
          if (!cname.includes('jobright') && !url.includes('jobright')) return false;
        } else if (selectedSourceFilter === 'TOPCV') {
          if (!cname.includes('topcv') && !url.includes('topcv')) return false;
        }
      }

      // Role Filter
      if (selectedRoleFilter !== 'ALL') {
        if (job.role_family !== selectedRoleFilter) return false;
      }

      // Seniority Filter
      if (selectedSeniorityFilter !== 'ALL') {
        const sen = (job.seniority || '').toLowerCase();
        if (selectedSeniorityFilter === 'junior') {
          if (sen !== 'junior' && sen !== 'intern' && sen !== 'entry') return false;
        } else if (selectedSeniorityFilter === 'senior') {
          if (sen !== 'senior' && sen !== 'lead' && sen !== 'staff' && sen !== 'principal') return false;
        } else if (selectedSeniorityFilter === 'mid') {
          if (sen !== 'mid') return false;
        } else {
          if (sen !== selectedSeniorityFilter.toLowerCase()) return false;
        }
      }

      // Remote Only
      if (remoteOnly) {
        const loc = (job.location || '').toLowerCase();
        const tit = (job.title || '').toLowerCase();
        const desc = (job.description_text || '').toLowerCase();
        const isRemote = (
          loc.includes('remote') ||
          loc.includes('[r]') ||
          tit.includes('remote') ||
          desc.includes('remote position') ||
          desc.includes('fully remote') ||
          desc.includes('100% remote') ||
          desc.includes('work from home')
        );
        if (!isRemote) return false;
      }

      return true;
    });
  }, [publicJobs, searchQuery, selectedSourceFilter, selectedRoleFilter, selectedSeniorityFilter, remoteOnly]);

  // Filtered Vault Jobs
  const filteredVaultJobs = useMemo(() => {
    if (!searchQuery) return lockedJobs;
    const q = searchQuery.toLowerCase();
    return lockedJobs.filter(
      (job) =>
        job.title.toLowerCase().includes(q) ||
        job.company_name.toLowerCase().includes(q) ||
        job.location.toLowerCase().includes(q)
    );
  }, [lockedJobs, searchQuery]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans pb-24">
      {/* Top Brand & Status Navigation */}
      <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-700 to-violet-600 flex items-center justify-center text-white font-black text-lg shadow-sm shadow-indigo-200">
              AI
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-heading font-black text-slate-900 text-lg tracking-tight">AI Job Intelligence</span>
                <span className="hidden sm:inline-block px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 uppercase tracking-wider">
                  Platform
                </span>
              </div>
              <p className="text-[11px] text-slate-500 hidden sm:block">Multi-Source ATS & Aggregator Intelligence Engine</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="hidden sm:inline">System Active & Ingesting</span>
              <span className="sm:hidden">Active</span>
            </div>

            <a
              href="https://github.com/vutl/Agent-Job-Crawler"
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-1.5 rounded-xl text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition flex items-center space-x-1.5"
            >
              <span>GitHub</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-8">
        {/* Executive Stats Banner */}
        <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="glass-card p-5 rounded-2xl flex flex-col justify-between">
            <div className="flex justify-between items-center text-slate-500 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider">Total Ingested</span>
              <div className="p-2 rounded-xl bg-indigo-50 text-indigo-600">
                <Database className="w-4 h-4" />
              </div>
            </div>
            <div>
              <div className="text-3xl font-black text-slate-900">{freshness?.total_jobs || publicJobs.length + lockedJobs.length}</div>
              <p className="text-xs text-slate-500 mt-1 flex items-center space-x-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                <span>100% SHA256 Deduplicated</span>
              </p>
            </div>
          </div>

          <div className="glass-card p-5 rounded-2xl flex flex-col justify-between">
            <div className="flex justify-between items-center text-slate-500 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider">Clean Public Jobs</span>
              <div className="p-2 rounded-xl bg-emerald-50 text-emerald-600">
                <Compass className="w-4 h-4" />
              </div>
            </div>
            <div>
              <div className="text-3xl font-black text-emerald-600">{publicJobs.length}</div>
              <p className="text-xs text-slate-500 mt-1">Verified Technical Roles</p>
            </div>
          </div>

          <div className="glass-card p-5 rounded-2xl flex flex-col justify-between">
            <div className="flex justify-between items-center text-slate-500 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider">Paywall Vault</span>
              <div className="p-2 rounded-xl bg-amber-50 text-amber-600">
                <Lock className="w-4 h-4" />
              </div>
            </div>
            <div>
              <div className="text-3xl font-black text-amber-600">{lockedJobs.length}</div>
              <p className="text-xs text-slate-500 mt-1">Gated / Login Wall Section</p>
            </div>
          </div>

          <div className="glass-card p-5 rounded-2xl flex flex-col justify-between">
            <div className="flex justify-between items-center text-slate-500 mb-2">
              <span className="text-xs font-bold uppercase tracking-wider">Connected ATS Monitors</span>
              <div className="p-2 rounded-xl bg-violet-50 text-violet-600">
                <Cpu className="w-4 h-4" />
              </div>
            </div>
            <div>
              <div className="text-3xl font-black text-slate-900">6 Platforms</div>
              <p className="text-xs text-slate-500 mt-1">Greenhouse, Lever, Workday, Foorilla, Jobright, TopCV</p>
            </div>
          </div>
        </section>

        {/* Main Navigation Tabs */}
        <div className="flex items-center justify-between border-b border-slate-200">
          <div className="flex space-x-2">
            <button
              onClick={() => setActiveTab('explorer')}
              className={`px-5 py-3 text-sm font-bold border-b-2 transition flex items-center space-x-2 ${
                activeTab === 'explorer'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <Compass className="w-4 h-4" />
              <span>AI Job Market Explorer</span>
              <span className="ml-1.5 px-2 py-0.5 rounded-full text-xs font-extrabold bg-indigo-50 text-indigo-700">
                {publicJobs.length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('blueprints')}
              className={`px-5 py-3 text-sm font-bold border-b-2 transition flex items-center space-x-2 ${
                activeTab === 'blueprints'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <Sparkles className="w-4 h-4 text-indigo-600 animate-pulse" />
              <span>Domain & Project Blueprints</span>
              <span className="ml-1.5 px-2 py-0.5 rounded-full text-[10px] font-black bg-gradient-to-r from-amber-500 to-rose-500 text-white uppercase tracking-wider">
                New
              </span>
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-5 py-3 text-sm font-bold border-b-2 transition flex items-center space-x-2 ${
                activeTab === 'analytics'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Tech Stack Analytics</span>
            </button>

            <button
              onClick={() => setActiveTab('vault')}
              className={`px-5 py-3 text-sm font-bold border-b-2 transition flex items-center space-x-2 ${
                activeTab === 'vault'
                  ? 'border-amber-600 text-amber-700'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <Lock className="w-4 h-4 text-amber-600" />
              <span>Paywall Vault</span>
              <span className="ml-1.5 px-2 py-0.5 rounded-full text-xs font-extrabold bg-amber-50 text-amber-800">
                {lockedJobs.length}
              </span>
            </button>
          </div>
        </div>

        {/* TAB 1: AI JOB MARKET EXPLORER */}
        {activeTab === 'explorer' && (
          <div className="space-y-6">
            {/* Search & Multi-Filter Control Box */}
            <div className="glass-card p-5 rounded-2xl space-y-4">
              <div className="flex flex-col md:flex-row gap-3 items-center">
                {/* Search Bar */}
                <div className="relative flex-1 w-full">
                  <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search by job title, company name, or tech skill (e.g. PyTorch, Kubernetes, Cloudflare)..."
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50/50 text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition"
                  />
                  {searchQuery && (
                    <button
                      onClick={() => setSearchQuery('')}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-1"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>

                {/* Source Filter Select */}
                <div className="flex items-center space-x-2 w-full md:w-auto">
                  <select
                    value={selectedSourceFilter}
                    onChange={(e) => setSelectedSourceFilter(e.target.value)}
                    className="w-full md:w-auto px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-800 text-xs font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                  >
                    <option value="ALL">🌐 All Sources</option>
                    <option value="DIRECT_ATS">🟢 Direct ATS (Cloudflare, Spotify, DataRobot)</option>
                    <option value="FOORILLA">🟣 Foorilla | Nokia & Partners</option>
                    <option value="JOBRIGHT">🔵 Jobright Aggregator</option>
                    <option value="TOPCV">🔴 TopCV Vietnam AI</option>
                  </select>

                  <select
                    value={selectedRoleFilter}
                    onChange={(e) => setSelectedRoleFilter(e.target.value)}
                    className="w-full md:w-auto px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-800 text-xs font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                  >
                    <option value="ALL">🎯 All Roles</option>
                    <option value="AI Engineer">AI Engineer</option>
                    <option value="ML Engineer">ML Engineer</option>
                    <option value="MLOps Engineer">MLOps Engineer</option>
                    <option value="Data Scientist">Data Scientist</option>
                  </select>

                  <select
                    value={selectedSeniorityFilter}
                    onChange={(e) => setSelectedSeniorityFilter(e.target.value)}
                    className="w-full md:w-auto px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white text-slate-800 text-xs font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                  >
                    <option value="ALL">⭐ All Seniority</option>
                    <option value="junior">Junior / New Grad</option>
                    <option value="mid">Mid-Level</option>
                    <option value="senior">Senior / Lead</option>
                  </select>
                </div>
              </div>

              {/* Quick Filters Pill Bar */}
              <div className="flex flex-wrap items-center justify-between pt-2 border-t border-slate-100 text-xs">
                <div className="flex items-center space-x-2">
                  <span className="text-slate-500 font-semibold">Showing:</span>
                  <span className="font-bold text-indigo-600">{filteredPublicJobs.length} active positions</span>
                  {selectedSourceFilter !== 'ALL' && (
                    <span className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 font-medium">
                      Source: {selectedSourceFilter}
                    </span>
                  )}
                </div>

                <label className="flex items-center space-x-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={remoteOnly}
                    onChange={(e) => setRemoteOnly(e.target.checked)}
                    className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="text-slate-700 font-semibold">🌍 Remote Only</span>
                </label>
              </div>
            </div>

            {/* Jobs Cards Grid */}
            {filteredPublicJobs.length === 0 ? (
              <div className="glass-card p-12 text-center rounded-2xl space-y-4 max-w-xl mx-auto">
                <Briefcase className="w-12 h-12 text-slate-300 mx-auto" />
                <div className="space-y-1">
                  <h3 className="font-heading font-bold text-lg text-slate-800">Không tìm thấy công việc khớp với bộ lọc</h3>
                  <p className="text-xs text-slate-500 max-w-md mx-auto">
                    {remoteOnly && selectedSourceFilter === 'JOBRIGHT'
                      ? 'Jobright hiện có nhiều vị trí Junior/Intern đặt tại trụ sở Mỹ (Palo Alto, New York, Austin, Chicago, Berkeley...). Bỏ chọn "Remote Only" để xem toàn bộ các vị trí này!'
                      : 'Hãy thử đổi nguồn tuyển dụng, bỏ chọn Remote Only hoặc xóa bớt từ khóa tìm kiếm.'}
                  </p>
                </div>

                <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
                  {remoteOnly && (
                    <button
                      onClick={() => setRemoteOnly(false)}
                      className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 transition"
                    >
                      🌍 Xem cả On-site / Hybrid (Bỏ Remote Only)
                    </button>
                  )}
                  {selectedSourceFilter !== 'ALL' && (
                    <button
                      onClick={() => setSelectedSourceFilter('ALL')}
                      className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-100 text-slate-800 hover:bg-slate-200 transition"
                    >
                      🌐 Xem tất cả nền tảng (Foorilla, Direct ATS, TopCV...)
                    </button>
                  )}
                  <button
                    onClick={() => {
                      setSearchQuery('');
                      setSelectedSourceFilter('ALL');
                      setSelectedRoleFilter('ALL');
                      setSelectedSeniorityFilter('ALL');
                      setRemoteOnly(false);
                    }}
                    className="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 text-white hover:bg-indigo-700 transition"
                  >
                    Reset toàn bộ bộ lọc
                  </button>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredPublicJobs.map((job) => {
                  const isFoorilla = job.company_name.toLowerCase().includes('foorilla');
                  const isJobright = job.company_name.toLowerCase().includes('jobright');
                  const isTopCV = job.company_name.toLowerCase().includes('topcv');

                  return (
                    <div
                      key={job.id}
                      className="glass-card glass-card-hover p-5 rounded-2xl flex flex-col justify-between space-y-4"
                    >
                      <div className="space-y-3">
                        {/* Header: Avatar, Company, Source Badges */}
                        <div className="flex items-start justify-between">
                          <div className="flex items-center space-x-3">
                            <div
                              className={`w-10 h-10 rounded-xl bg-gradient-to-tr ${getCompanyAvatarGradient(
                                job.company_name
                              )} text-white font-bold text-sm flex items-center justify-center shadow-sm`}
                            >
                              {getInitials(job.company_name)}
                            </div>
                            <div>
                              <h4 className="font-bold text-slate-900 text-sm leading-tight flex items-center space-x-1.5">
                                <span>{job.company_name}</span>
                              </h4>
                              <p className="text-xs text-slate-500 flex items-center space-x-1 mt-0.5">
                                <MapPin className="w-3 h-3 text-slate-400" />
                                <span className="line-clamp-1">{job.location || 'Distributed'}</span>
                              </p>
                            </div>
                          </div>

                          <div className="flex flex-col items-end space-y-1">
                            {/* Source Badge */}
                            {isFoorilla ? (
                              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-purple-50 text-purple-700 border border-purple-200">
                                Foorilla Direct
                              </span>
                            ) : isJobright ? (
                              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-50 text-blue-700 border border-blue-200">
                                Jobright
                              </span>
                            ) : isTopCV ? (
                              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-rose-50 text-rose-700 border border-rose-200">
                                TopCV.vn
                              </span>
                            ) : (
                              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-50 text-emerald-700 border border-emerald-200">
                                Live Direct ATS
                              </span>
                            )}

                            <span className="text-[10px] text-slate-400 font-medium flex items-center space-x-1">
                              <Clock className="w-3 h-3" />
                              <span>{job.posted_time_ago || 'Recently'}</span>
                            </span>
                          </div>
                        </div>

                        {/* Title */}
                        <h3 className="font-heading font-bold text-slate-900 text-base leading-snug line-clamp-2 hover:text-indigo-600 transition">
                          {job.title}
                        </h3>

                        {/* Tags: Role Family & Seniority */}
                        <div className="flex flex-wrap gap-1.5 text-xs">
                          <span className="px-2.5 py-0.5 rounded-lg font-bold bg-indigo-50 text-indigo-700 border border-indigo-100 text-[11px]">
                            {job.role_family || 'AI Engineer'}
                          </span>
                          <span className="px-2 py-0.5 rounded-lg font-semibold bg-slate-100 text-slate-700 text-[11px] capitalize">
                            {job.seniority || 'Mid'}
                          </span>
                        </div>

                        {/* Extracted Skills Chips */}
                        {job.skills && job.skills.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 pt-1">
                            {job.skills.slice(0, 4).map((s) => (
                              <span
                                key={s.name}
                                className="px-2 py-0.5 rounded-md text-[11px] font-medium bg-slate-50 border border-slate-200 text-slate-700"
                              >
                                {s.name}
                              </span>
                            ))}
                            {job.skills.length > 4 && (
                              <span className="px-1.5 py-0.5 rounded-md text-[10px] font-semibold text-slate-400 bg-slate-100">
                                +{job.skills.length - 4} more
                              </span>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Card Action Buttons */}
                      <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                        <button
                          onClick={() => setSelectedJobModal(job)}
                          className="inline-flex items-center space-x-1.5 text-xs font-bold text-indigo-600 hover:text-indigo-800 transition py-1"
                        >
                          <BookOpen className="w-3.5 h-3.5" />
                          <span>Xem chi tiết JD</span>
                        </button>

                        {isJobright ? (
                          <div className="flex items-center space-x-1.5">
                            <a
                              href={
                                job.external_id && job.external_id.length > 10
                                  ? `https://jobright.ai/jobs/info/${job.external_id}#overview`
                                  : job.canonical_url
                              }
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-xl text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 transition shadow-sm"
                              title="Mở trực tiếp trên Jobright"
                            >
                              <span>Jobright ↗</span>
                            </a>
                            {job.canonical_url && !job.canonical_url.includes('jobright.ai') && (
                              <a
                                href={job.canonical_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-900 hover:bg-indigo-600 text-white transition shadow-sm"
                                title="Ứng tuyển trên cổng gốc"
                              >
                                <span>Apply ↗</span>
                              </a>
                            )}
                          </div>
                        ) : (
                          <a
                            href={job.canonical_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-900 hover:bg-indigo-600 text-white transition shadow-sm"
                          >
                            <span>Apply on Portal</span>
                            <ArrowUpRight className="w-3.5 h-3.5" />
                          </a>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* TAB: DOMAIN & CAPSTONE PROJECT BLUEPRINTS */}
        {activeTab === 'blueprints' && (
          <div className="space-y-8 animate-in fade-in duration-300">
            {/* Banner Header */}
            <div className="glass-card p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-900/90 via-slate-900/95 to-indigo-950/90 text-white relative overflow-hidden border border-indigo-500/20 shadow-xl">
              <div className="absolute right-0 top-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
              <div className="relative z-10 space-y-3 max-w-3xl">
                <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-indigo-200 text-xs font-bold tracking-wide">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                  <span>PRODUCTION-GRADE CAPSTONE BLUEPRINTS & DOMAIN INTELLIGENCE</span>
                </div>
                <h2 className="font-heading font-black text-2xl sm:text-3xl text-white tracking-tight leading-tight">
                  Chiến Lược Project & Ma Trận Kỹ Năng Theo Lĩnh Vực (Intern / New Grad / Junior)
                </h2>
                <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
                  Được bóc tách từ 513+ bài tuyển dụng thực tế (Qualcomm, JPMorgan, Mozilla, Spotify, Nokia Bell Labs, DataRobot,...). Khám phá chính xác bài toán các công ty đang giải quyết và bản thiết kế các giải pháp / product đột phá giúp bạn vượt trội 99% ứng viên khi phỏng vấn.
                </p>
              </div>
            </div>

            {/* Domain Selector Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {domainIntelligence.map((domain) => {
                const isSelected = selectedDomainId === domain.id;
                return (
                  <button
                    key={domain.id}
                    onClick={() => setSelectedDomainId(domain.id)}
                    className={`p-4 rounded-2xl text-left transition-all duration-200 flex flex-col justify-between space-y-3 border ${
                      isSelected
                        ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-200 scale-[1.02]'
                        : 'glass-card text-slate-700 hover:border-indigo-300 hover:bg-slate-50/80'
                    }`}
                  >
                    <div className="flex items-center justify-between w-full">
                      <div
                        className={`p-2.5 rounded-xl ${
                          isSelected ? 'bg-white/20 text-white' : 'bg-indigo-50 text-indigo-600'
                        }`}
                      >
                        {domain.id === 'agentic-ai' ? (
                          <Bot className="w-5 h-5" />
                        ) : domain.id === 'computer-vision' ? (
                          <Eye className="w-5 h-5" />
                        ) : domain.id === 'healthcare-ai' ? (
                          <HeartPulse className="w-5 h-5" />
                        ) : domain.id === 'fintech-ai' ? (
                          <CreditCard className="w-5 h-5" />
                        ) : domain.id === 'mlops-platform' ? (
                          <Cpu className="w-5 h-5" />
                        ) : (
                          <Search className="w-5 h-5" />
                        )}
                      </div>
                      <span
                        className={`text-[9px] font-extrabold px-2 py-0.5 rounded-full ${
                          isSelected ? 'bg-white text-indigo-900' : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {domain.badge}
                      </span>
                    </div>
                    <div>
                      <h4 className="font-bold text-xs sm:text-sm leading-snug line-clamp-2">
                        {domain.title}
                      </h4>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Selected Domain Deep Dive */}
            {(() => {
              const activeDomain = domainIntelligence.find((d) => d.id === selectedDomainId) || domainIntelligence[0];
              if (!activeDomain) return null;

              return (
                <div className="space-y-6 animate-in fade-in duration-200">
                  {/* Domain Header Card */}
                  <div className="glass-card p-6 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-l-4 border-l-indigo-600">
                    <div className="space-y-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="font-heading font-black text-xl text-slate-900">
                          {activeDomain.title}
                        </h3>
                        <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-indigo-50 text-indigo-700 border border-indigo-200">
                          {activeDomain.badge}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 font-medium">{activeDomain.tagline}</p>
                    </div>

                    <div className="flex flex-wrap gap-1.5 items-center">
                      <span className="text-xs font-bold text-slate-400 mr-1">Target Roles:</span>
                      {activeDomain.target_roles.map((r) => (
                        <span
                          key={r}
                          className="px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-900 text-white"
                        >
                          {r}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Grid 2 Columns: Real-World Industry Context & Intern/Junior Expectation Matrix */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Column 1: Real-World Industry Context & Tasks */}
                    <div className="glass-card p-6 rounded-2xl space-y-5 flex flex-col justify-between">
                      <div className="space-y-4">
                        <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
                          <div className="p-2 rounded-xl bg-blue-50 text-blue-600">
                            <Building2 className="w-5 h-5" />
                          </div>
                          <div>
                            <h4 className="font-bold text-slate-900 text-sm">
                              1. Bài Toán & Product Thực Tế Doanh Nghiệp Đang Xây Dựng
                            </h4>
                            <p className="text-[11px] text-slate-500">
                              Những nhiệm vụ sản xuất thực chiến bóc tách từ JD các tập đoàn lớn
                            </p>
                          </div>
                        </div>

                        <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-xl border border-slate-100 italic">
                          "{activeDomain.industry_context.summary}"
                        </p>

                        <div className="space-y-2">
                          <span className="text-xs font-extrabold uppercase tracking-wider text-slate-400">
                            Các công ty tiêu biểu đang tuyển dụng:
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {activeDomain.industry_context.companies_hiring.map((co) => (
                              <span
                                key={co}
                                className="px-2.5 py-1 rounded-lg text-xs font-bold bg-blue-50 text-blue-700 border border-blue-100"
                              >
                                {co}
                              </span>
                            ))}
                          </div>
                        </div>

                        <div className="space-y-2 pt-2">
                          <span className="text-xs font-extrabold uppercase tracking-wider text-slate-400">
                            Nhiệm vụ & bài toán cốt lõi trong JD:
                          </span>
                          <ul className="space-y-2">
                            {activeDomain.industry_context.real_world_tasks.map((task, idx) => (
                              <li key={idx} className="text-xs text-slate-700 flex items-start space-x-2 bg-white p-2.5 rounded-xl border border-slate-100 shadow-sm">
                                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                                <span>{task}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>

                    {/* Column 2: Intern / Junior Practical Must-Haves */}
                    <div className="glass-card p-6 rounded-2xl space-y-5 flex flex-col justify-between">
                      <div className="space-y-4">
                        <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
                          <div className="p-2 rounded-xl bg-purple-50 text-purple-600">
                            <Award className="w-5 h-5" />
                          </div>
                          <div>
                            <h4 className="font-bold text-slate-900 text-sm">
                              2. Yêu Cầu Thực Chiến Cần Hiểu Sâu (Intern / Junior Level)
                            </h4>
                            <p className="text-[11px] text-slate-500">
                              Không chỉ học vẹt syntax, mà cần nắm vững bản chất kiến trúc & trade-offs
                            </p>
                          </div>
                        </div>

                        {/* Core Theories */}
                        <div className="space-y-2">
                          <span className="text-xs font-extrabold uppercase tracking-wider text-purple-700 flex items-center space-x-1">
                            <Lightbulb className="w-3.5 h-3.5" />
                            <span>Nền tảng lý thuyết & Bản chất kiến trúc:</span>
                          </span>
                          <ul className="space-y-1.5">
                            {activeDomain.intern_junior_expectations.core_theories.map((theory, idx) => (
                              <li key={idx} className="text-xs text-slate-700 flex items-start space-x-2">
                                <span className="text-purple-600 font-bold">•</span>
                                <span>{theory}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Engineering Toolkit */}
                        <div className="space-y-2 pt-2 border-t border-slate-100">
                          <span className="text-xs font-extrabold uppercase tracking-wider text-indigo-700 flex items-center space-x-1">
                            <Code2 className="w-3.5 h-3.5" />
                            <span>Kỹ năng & Toolkit Kỹ nghệ Sản xuất:</span>
                          </span>
                          <ul className="space-y-1.5">
                            {activeDomain.intern_junior_expectations.engineering_skills.map((skill, idx) => (
                              <li key={idx} className="text-xs text-slate-700 flex items-start space-x-2">
                                <span className="text-indigo-600 font-bold">•</span>
                                <span>{skill}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Cost / Latency Trade-offs */}
                        <div className="space-y-2 pt-2 border-t border-slate-100">
                          <span className="text-xs font-extrabold uppercase tracking-wider text-emerald-700 flex items-center space-x-1">
                            <Zap className="w-3.5 h-3.5" />
                            <span>Cân nhắc Đánh đổi Chi phí / Độ trễ (Trade-offs):</span>
                          </span>
                          <ul className="space-y-1.5">
                            {activeDomain.intern_junior_expectations.cost_latency_tradeoffs.map((t, idx) => (
                              <li key={idx} className="text-xs text-slate-700 flex items-start space-x-2">
                                <span className="text-emerald-600 font-bold">•</span>
                                <span>{t}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Section 3: "Hiring Magnet" Capstone Project Blueprint */}
                  <div className="glass-card p-6 sm:p-8 rounded-3xl space-y-6 border-2 border-indigo-500/30 bg-gradient-to-br from-white via-indigo-50/20 to-white shadow-xl">
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-indigo-100 pb-4">
                      <div className="space-y-1">
                        <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-indigo-600 text-white text-xs font-black tracking-wide shadow-sm">
                          <Rocket className="w-3.5 h-3.5" />
                          <span>3. "HIRING MAGNET" CAPSTONE PROJECT BLUEPRINT</span>
                        </div>
                        <h3 className="font-heading font-black text-2xl text-slate-900">
                          {activeDomain.capstone_blueprint.project_name}
                        </h3>
                      </div>

                      <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center space-x-1">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
                        <span>Production Ready Architecture</span>
                      </span>
                    </div>

                    {/* Value Prop & Problem */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-4 rounded-2xl bg-indigo-50/50 border border-indigo-100 space-y-1.5">
                        <span className="text-xs font-extrabold text-indigo-900 uppercase tracking-wider flex items-center space-x-1">
                          <Target className="w-3.5 h-3.5 text-indigo-600" />
                          <span>Giá trị Đột phá & Định vị Sản phẩm:</span>
                        </span>
                        <p className="text-xs text-slate-800 leading-relaxed font-medium">
                          {activeDomain.capstone_blueprint.value_prop}
                        </p>
                      </div>

                      <div className="p-4 rounded-2xl bg-rose-50/50 border border-rose-100 space-y-1.5">
                        <span className="text-xs font-extrabold text-rose-900 uppercase tracking-wider flex items-center space-x-1">
                          <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
                          <span>Nút thắt Sản xuất Đang Giải Quyết (Pain Point):</span>
                        </span>
                        <p className="text-xs text-slate-800 leading-relaxed font-medium">
                          {activeDomain.capstone_blueprint.core_problem}
                        </p>
                      </div>
                    </div>

                    {/* System Architecture Flow */}
                    <div className="space-y-3">
                      <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-700 flex items-center space-x-1.5">
                        <Layers className="w-4 h-4 text-indigo-600" />
                        <span>Bản Vẽ Luồng Kiến Trúc Hệ Thống (End-to-End System Workflow):</span>
                      </h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                        {activeDomain.capstone_blueprint.system_architecture.map((step, idx) => (
                          <div
                            key={idx}
                            className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-2 flex flex-col justify-between hover:border-indigo-400 transition"
                          >
                            <div className="flex justify-between items-center">
                              <span className="w-6 h-6 rounded-full bg-indigo-600 text-white font-black text-xs flex items-center justify-center">
                                {idx + 1}
                              </span>
                              <span className="text-[10px] font-bold text-slate-400 uppercase">Component</span>
                            </div>
                            <p className="text-xs text-slate-800 leading-relaxed">
                              {step}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Key SLA & Benchmark Metrics to Show */}
                    <div className="p-5 rounded-2xl bg-slate-900 text-white space-y-3">
                      <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                        <span className="text-xs font-extrabold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
                          <TrendingUp className="w-4 h-4" />
                          <span>Chỉ Số Đo Lường & SLA Cần Trưng Bày Trên CV / GitHub:</span>
                        </span>
                        <span className="text-[11px] text-slate-400">Quantitative Proof of Quality</span>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
                        {activeDomain.capstone_blueprint.key_metrics_to_show.map((m, idx) => (
                          <div key={idx} className="p-3 rounded-xl bg-slate-800/80 border border-slate-700 text-xs flex items-center space-x-2">
                            <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                            <span className="font-semibold text-slate-200">{m}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Standout Factor */}
                    <div className="p-5 rounded-2xl bg-gradient-to-r from-amber-500/10 via-orange-500/10 to-amber-500/10 border border-amber-200/80 flex items-start space-x-3 text-amber-950">
                      <Flame className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                      <div className="space-y-1 text-xs">
                        <h5 className="font-extrabold text-amber-900">
                          🌟 Vì Sao Dự Án Này Giúp Bạn Đánh Bại 99% Ứng Viên Khác (The Standout Factor):
                        </h5>
                        <p className="text-slate-800 leading-relaxed font-medium">
                          {activeDomain.capstone_blueprint.standout_factor}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        )}

        {/* TAB 2: TECH STACK ANALYTICS */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="glass-card p-6 rounded-2xl space-y-6">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-100 pb-4">
                <div>
                  <h3 className="font-heading font-black text-xl text-slate-900">Tech Stack Demand by Target Role</h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Extracted requirements and preferred technology frequencies from analyzed postings.
                  </p>
                </div>

                <div className="flex flex-wrap gap-2">
                  {ROLES.map((role) => (
                    <button
                      key={role}
                      onClick={() => setSelectedRole(role)}
                      className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition ${
                        selectedRole === role
                          ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-200'
                          : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                      }`}
                    >
                      {role}
                    </button>
                  ))}
                </div>
              </div>

              {/* Skills Bar Chart List */}
              <div className="space-y-4">
                {skills.length === 0 ? (
                  <p className="text-center text-slate-400 py-8 text-xs">Loading analytics for {selectedRole}...</p>
                ) : (
                  skills.map((s, idx) => (
                    <div key={s.name} className="space-y-1.5">
                      <div className="flex justify-between items-center text-xs">
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-[11px] font-bold text-slate-400">#{idx + 1}</span>
                          <span className="font-bold text-slate-900">{s.name}</span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-600 uppercase">
                            {s.category}
                          </span>
                        </div>
                        <div className="flex items-center space-x-3 text-slate-600">
                          <span className="text-[11px]">{s.count} mentions</span>
                          <span className="font-extrabold text-indigo-600">{Math.round(s.share * 100)}%</span>
                        </div>
                      </div>

                      <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden flex">
                        <div
                          className="h-full bg-indigo-600 rounded-l-full"
                          style={{ width: `${Math.round(s.share * 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: PAYWALL & PROTECTED VAULT */}
        {activeTab === 'vault' && (
          <div className="space-y-6">
            <div className="bg-amber-50/70 border border-amber-200 p-5 rounded-2xl flex items-start space-x-3 text-amber-900">
              <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div className="text-xs space-y-1">
                <h4 className="font-bold">Protected / Login Wall Audit Section ({lockedJobs.length} Jobs)</h4>
                <p className="text-amber-800 leading-relaxed">
                  These postings were discovered by monitors but require user accounts, subscription logins, or corporate portal authentication. They are archived here with 0 LLM token cost to protect public data cleanliness.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredVaultJobs.map((job) => (
                <div key={job.id} className="glass-card p-5 rounded-2xl space-y-3 border-amber-200">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 uppercase tracking-wider">
                        Protected / Login Required
                      </span>
                      <h4 className="font-bold text-slate-900 text-sm mt-1">{job.title}</h4>
                      <p className="text-xs text-slate-500">{job.company_name} • {job.location}</p>
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 line-clamp-2 bg-slate-50 p-3 rounded-xl border border-slate-100 italic">
                    {job.description_text || 'Requires login credentials to inspect full job description.'}
                  </p>

                  <div className="pt-2 flex justify-between items-center border-t border-slate-100">
                    <span className="text-[10px] text-slate-400">ID: {job.id}</span>
                    <a
                      href={job.canonical_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center space-x-1 text-xs font-bold text-amber-700 hover:text-amber-900"
                    >
                      <span>View Login Portal</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* DETAIL MODAL (Xem chi tiết JD) */}
      {selectedJobModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="glass-card w-full max-w-4xl max-h-[90vh] rounded-3xl shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200 border-slate-200">
            {/* Modal Header */}
            <div className="p-6 border-b border-slate-100 flex justify-between items-start bg-slate-50/50">
              <div className="space-y-2 pr-4">
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <span className="px-3 py-1 rounded-lg font-extrabold bg-indigo-50 text-indigo-700 border border-indigo-200">
                    {selectedJobModal.role_family} ({selectedJobModal.seniority.toUpperCase()})
                  </span>
                  <span className="px-2.5 py-1 rounded-lg text-slate-500 bg-white border border-slate-200 font-semibold flex items-center space-x-1">
                    <Clock className="w-3 h-3 text-slate-400" />
                    <span>{selectedJobModal.posted_time_ago || 'Recently posted'}</span>
                  </span>
                </div>

                <h2 className="font-heading font-black text-2xl text-slate-900 leading-tight">
                  {selectedJobModal.title}
                </h2>

                <div className="flex flex-wrap items-center gap-4 text-xs font-semibold text-slate-600">
                  <span className="flex items-center space-x-1.5 text-slate-900">
                    <Building2 className="w-4 h-4 text-indigo-600" />
                    <span>{selectedJobModal.company_name}</span>
                  </span>
                  <span className="flex items-center space-x-1.5 text-slate-500">
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

            {/* Modal Scrollable Body */}
            <div className="p-6 overflow-y-auto space-y-6 flex-1">
              {/* Extracted Skills & Evidence Spans */}
              <div className="p-5 rounded-2xl bg-indigo-50/40 border border-indigo-100 space-y-3">
                <h4 className="text-xs uppercase tracking-wider text-indigo-900 font-extrabold flex items-center space-x-2">
                  <Award className="w-4 h-4 text-indigo-600" />
                  <span>Extracted Tech Stack & LLM Evidence Spans</span>
                </h4>

                {selectedJobModal.skills && selectedJobModal.skills.length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {selectedJobModal.skills.map((s) => (
                      <div
                        key={s.name}
                        className="p-3.5 rounded-xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between space-y-1"
                      >
                        <div className="flex justify-between items-center">
                          <span className="font-bold text-slate-900 text-sm">{s.name}</span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-emerald-50 text-emerald-700 border border-emerald-200 uppercase">
                            {s.requirement_type || 'REQUIRED'}
                          </span>
                        </div>
                        {s.evidence_text && (
                          <p className="text-[11px] text-slate-500 italic line-clamp-2">
                            "{s.evidence_text}"
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-400 italic">No specific framework skills extracted.</p>
                )}
              </div>

              {/* Formatted Markdown Job Description Body */}
              <div className="space-y-3">
                <h4 className="text-xs uppercase tracking-wider text-slate-500 font-bold">
                  Description
                </h4>
                <div className="p-6 rounded-2xl bg-white border border-slate-200">
                  <MarkdownJDViewer content={selectedJobModal.description_text} />
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-5 border-t border-slate-100 bg-slate-50/50 flex flex-wrap justify-between items-center gap-3">
              <button
                onClick={() => setSelectedJobModal(null)}
                className="px-5 py-2.5 rounded-xl text-xs font-bold text-slate-600 hover:text-slate-900 hover:bg-slate-200 transition"
              >
                Close Panel
              </button>

              <div className="flex flex-wrap items-center gap-2">
                {/* Jobright Direct Deep-links if applicable */}
                {getValidJobrightUrl(selectedJobModal.external_id, selectedJobModal.canonical_url, selectedJobModal.description_text) && (
                  <>
                    <a
                      href={getValidJobrightUrl(selectedJobModal.external_id, selectedJobModal.canonical_url, selectedJobModal.description_text)!}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center space-x-1.5 px-4 py-2.5 rounded-xl text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 shadow-sm transition"
                    >
                      <span>🔍 Jobright Overview & Match</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </a>

                    <a
                      href={getValidJobrightUrl(selectedJobModal.external_id, selectedJobModal.canonical_url, selectedJobModal.description_text)!.replace('#overview', '#company')}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center space-x-1.5 px-3.5 py-2.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-700 hover:bg-slate-200 transition"
                    >
                      <span>🏢 Jobright Company Info</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </a>
                  </>
                )}

                {/* Direct Official Apply Portal if different from Jobright */}
                {selectedJobModal.canonical_url && !selectedJobModal.canonical_url.includes('jobright.ai') && (
                  <a
                    href={selectedJobModal.canonical_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm shadow-indigo-200 transition"
                  >
                    <span>Apply on Official Portal (Original Post)</span>
                    <ArrowUpRight className="w-4 h-4" />
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
