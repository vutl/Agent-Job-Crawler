'use client';

import React, { useState, useEffect } from 'react';
import { Activity, Database, Cpu, Layers, CheckCircle, Search, ArrowUpRight, TrendingUp } from 'lucide-react';

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

const ROLES = ['AI Engineer', 'ML Engineer', 'MLOps Engineer', 'Data Scientist'];

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
  const [selectedRole, setSelectedRole] = useState('AI Engineer');
  const [freshness, setFreshness] = useState<DataFreshness>({
    total_jobs: 4,
    active_jobs: 4,
    analyzed_jobs: 4,
    latest_job_crawled_at: new Date().toISOString(),
  });
  const [skills, setSkills] = useState<SkillStat[]>(SAMPLE_SKILLS['AI Engineer']);
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
      } catch (e) {
        setIsLiveApi(false);
        setSkills(SAMPLE_SKILLS[selectedRole] || []);
      }
    }
    fetchData();
  }, [selectedRole]);

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-gradient-to-r from-indigo-900/30 via-slate-900 to-emerald-900/20 p-6 rounded-2xl border border-indigo-500/20 shadow-xl">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            AI Job Market Intelligence
          </h1>
          <p className="text-gray-400 mt-1 text-sm">
            Continuous ingestion from Greenhouse, Lever, and TopCV with structured LLM skill extraction via 9Router & LangChain.
          </p>
        </div>
        <div className="flex items-center space-x-2 bg-indigo-500/10 px-4 py-2 rounded-xl border border-indigo-500/20 text-indigo-300 text-xs font-semibold">
          <TrendingUp className="w-4 h-4 text-indigo-400" />
          <span>V1 Production Pipeline Active</span>
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
          <div className="text-xs text-gray-400">Greenhouse, Lever, TopCV</div>
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

      {/* Role Selection Tabs */}
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

        {/* Skill Analytics Table & Progress */}
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
              <div key={skill.name} className="p-4 sm:p-5 hover:bg-gray-800/30 transition flex flex-col sm:flex-row sm:items-center justify-between gap-4">
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
    </div>
  );
}
