"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ShieldCheck, Sparkles } from "lucide-react";
import { apiFetch, setToken } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const presets = {
  manager: { email: "manager@fieldops.ai", password: "manager123" },
  dispatcher: { email: "dispatcher@fieldops.ai", password: "dispatcher123" },
  analyst: { email: "analyst@fieldops.ai", password: "analyst123" },
};

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState(presets.manager.email);
  const [password, setPassword] = useState(presets.manager.password);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await apiFetch<{ access_token: string }>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      setToken(data.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <section className="relative hidden overflow-hidden bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 p-10 text-white lg:block">
        <div className="absolute -left-14 top-10 h-56 w-56 rounded-full bg-cyan-400/20 blur-3xl" />
        <div className="absolute -right-12 bottom-12 h-64 w-64 rounded-full bg-indigo-400/25 blur-3xl" />
        <div className="relative z-10 max-w-xl">
          <p className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs uppercase tracking-[0.16em]">
            <Sparkles size={13} /> FIELDOPS SENTINEL AI
          </p>
          <h1 className="mt-6 font-display text-4xl font-bold leading-tight">Operational Loss Prevention Engine for field service operations.</h1>
          <p className="mt-4 text-sm text-slate-200">
            Predict SLA leakage, prioritize interventions, enforce policies, and keep humans in control with a full audit trail.
          </p>
        </div>
      </section>

      <section className="flex items-center justify-center p-6">
        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} className="panel w-full max-w-md p-8">
          <h2 className="font-display text-2xl font-bold text-slate-900">Sign In</h2>
          <p className="mt-1 text-sm text-slate-500">Access the command center with a demo role.</p>

          <div className="mt-5 flex flex-wrap gap-2">
            {Object.entries(presets).map(([role, creds]) => (
              <button
                key={role}
                className="rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-600 hover:bg-slate-100"
                onClick={() => {
                  setEmail(creds.email);
                  setPassword(creds.password);
                }}
                type="button"
              >
                {role}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="mt-6 space-y-3">
            <Input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <Input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
            {error && <p className="text-sm text-red-600">{error}</p>}
            <Button className="w-full" disabled={loading}>{loading ? "Signing in..." : "Enter Command Center"}</Button>
          </form>
          <p className="mt-4 inline-flex items-center gap-1 text-xs text-slate-500"><ShieldCheck size={13} /> Critical actions require human approval</p>
        </motion.div>
      </section>
    </div>
  );
}
