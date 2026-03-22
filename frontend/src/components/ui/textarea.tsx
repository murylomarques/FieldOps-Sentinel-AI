"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export function Textarea(props: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea {...props} className={cn("w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-primary", props.className)} />;
}
