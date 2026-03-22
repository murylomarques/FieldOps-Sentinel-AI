"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "secondary" | "danger" | "ghost";
}

export function Button({ className, variant = "default", ...props }: ButtonProps) {
  const style = {
    default: "bg-primary text-white hover:bg-blue-800",
    secondary: "bg-secondary text-white hover:bg-teal-800",
    danger: "bg-red-600 text-white hover:bg-red-700",
    ghost: "bg-transparent text-slate-700 hover:bg-slate-100",
  }[variant];

  return (
    <button
      className={cn("inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold transition", style, className)}
      {...props}
    />
  );
}

