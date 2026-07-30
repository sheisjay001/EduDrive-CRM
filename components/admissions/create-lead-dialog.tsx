"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import type { LeadCreateRequest } from "@/types/crm";

const leadSchema = z.object({
  firstName: z.string().min(1, "First name is required"),
  lastName: z.string().min(1, "Last name is required"),
  parentName: z.string().min(1, "Parent name is required"),
  parentPhone: z.string().min(10, "Phone number is required"),
  parentEmail: z.string().email("Invalid email").optional().or(z.literal("")),
  source: z.string().min(1, "Source is required"),
  stage: z.string().min(1, "Stage is required"),
  interestedClass: z.string().optional(),
  followUpAt: z.string().optional(),
});

type LeadFormValues = z.infer<typeof leadSchema>;

interface CreateLeadDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: LeadCreateRequest) => void;
}

const SOURCES = ["website", "walk_in", "referral", "social_media", "campaign", "manual"];
const STAGES = ["new", "contacted", "tour_scheduled", "assessment_booked", "offered"];
const CLASSES = ["JSS 1", "JSS 2", "JSS 3", "SS 1", "SS 2", "SS 3"];

export function CreateLeadDialog({ open, onOpenChange, onSubmit }: CreateLeadDialogProps) {
  const form = useForm<LeadFormValues>({
    resolver: zodResolver(leadSchema),
    defaultValues: {
      firstName: "",
      lastName: "",
      parentName: "",
      parentPhone: "",
      parentEmail: "",
      source: "manual",
      stage: "new",
      interestedClass: "",
      followUpAt: "",
    },
  });

  const handleSubmit = form.handleSubmit((data) => {
    const payload: LeadCreateRequest = {
      firstName: data.firstName,
      lastName: data.lastName,
      parentName: data.parentName,
      parentPhone: data.parentPhone,
      parentEmail: data.parentEmail || undefined,
      source: data.source,
      stage: data.stage,
      interestedClass: data.interestedClass || undefined,
      followUpAt: data.followUpAt || undefined,
    };
    onSubmit(payload);
    form.reset();
    onOpenChange(false);
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create new lead</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>First name</Label>
              <Input {...form.register("firstName")} placeholder="Child's first name" />
              {form.formState.errors.firstName && (
                <p className="mt-1 text-xs text-rose-200">{form.formState.errors.firstName.message}</p>
              )}
            </div>
            <div>
              <Label>Last name</Label>
              <Input {...form.register("lastName")} placeholder="Child's last name" />
              {form.formState.errors.lastName && (
                <p className="mt-1 text-xs text-rose-200">{form.formState.errors.lastName.message}</p>
              )}
            </div>
          </div>

          <div>
            <Label>Parent name</Label>
            <Input {...form.register("parentName")} placeholder="Parent or guardian name" />
            {form.formState.errors.parentName && (
              <p className="mt-1 text-xs text-rose-200">{form.formState.errors.parentName.message}</p>
            )}
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>Phone number</Label>
              <Input {...form.register("parentPhone")} placeholder="+234..." />
              {form.formState.errors.parentPhone && (
                <p className="mt-1 text-xs text-rose-200">{form.formState.errors.parentPhone.message}</p>
              )}
            </div>
            <div>
              <Label>Email (optional)</Label>
              <Input {...form.register("parentEmail")} placeholder="parent@example.com" />
              {form.formState.errors.parentEmail && (
                <p className="mt-1 text-xs text-rose-200">{form.formState.errors.parentEmail.message}</p>
              )}
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>Source</Label>
              <Select {...form.register("source")}>
                {SOURCES.map((source) => (
                  <option key={source} value={source}>
                    {source.replace("_", " ").toUpperCase()}
                  </option>
                ))}
              </Select>
            </div>
            <div>
              <Label>Stage</Label>
              <Select {...form.register("stage")}>
                {STAGES.map((stage) => (
                  <option key={stage} value={stage}>
                    {stage.replace("_", " ").toUpperCase()}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          <div>
            <Label>Interested class (optional)</Label>
            <Select {...form.register("interestedClass")}>
              <option value="">Select class</option>
              {CLASSES.map((cls) => (
                <option key={cls} value={cls}>
                  {cls}
                </option>
              ))}
            </Select>
          </div>

          <div>
            <Label>Follow-up date (optional)</Label>
            <Input type="datetime-local" {...form.register("followUpAt")} />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit">Create lead</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
