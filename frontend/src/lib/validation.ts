import { z } from "zod";

/** Mirrors `PHONE_REGEX` in the backend's `core/validators.py`. */
export const PHONE_REGEX = /^\+?[0-9\s\-()]{7,20}$/;

export const phoneNumberField = z
  .string()
  .min(7, "Enter a valid phone number")
  .regex(PHONE_REGEX, "Enter a valid phone number");

export const emailField = z.string().min(1, "Email is required").email("Enter a valid email address");

export const requiredField = (label: string) => z.string().min(1, `${label} is required`);

export const estimatedValueField = z.coerce.number().positive("Value must be greater than zero");

export const expectedClosingDateField = requiredField("Expected closing date");
