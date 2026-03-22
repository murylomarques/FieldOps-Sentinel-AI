"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
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
    <div className="flex min-h-screen items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="panel w-full max-w-md p-8"
      >
        <h1 className="font-display text-2xl font-bold">FIELDOPS SENTINEL AI</h1>
        <p className="mt-2 text-sm text-slate-500">Agentic operations intelligence platform for field service teams.</p>

        <div className="mt-5 flex gap-2">
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
          <Button className="w-full" disabled={loading}>{loading ? "Signing in..." : "Sign in"}</Button>
        </form>
      </motion.div>
    </div>
  );
}
