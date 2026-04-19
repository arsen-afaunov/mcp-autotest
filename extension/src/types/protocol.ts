import { z } from 'zod';

export const REQUEST_TYPES = {
  CLICK: 'click',
  RUN: 'run',
  REGISTER: 'register',
} as const;

export type RequestType = keyof typeof REQUEST_TYPES;

export const BaseRequestSchema = z.object({
  id: z.string(),
});

export const ClickPayloadSchema = z.object({
  selector: z.string(),
});

export const RunPayloadSchema = z.object({
  script: z.string(),
});

export const RegisterPayloadSchema = z.null();

export const ClickCommandSchema = BaseRequestSchema.extend({
  type: z.literal(REQUEST_TYPES.CLICK),
  payload: ClickPayloadSchema,
});

export const RunCommandSchema = BaseRequestSchema.extend({
  type: z.literal(REQUEST_TYPES.RUN),
  payload: RunPayloadSchema,
});

export const RegisterCommandSchema = BaseRequestSchema.extend({
  type: z.literal(REQUEST_TYPES.REGISTER),
  payload: RegisterPayloadSchema,
});

export const McpRequestSchema = z.union([
  ClickCommandSchema,
  RunCommandSchema,
  RegisterCommandSchema,
]);

export type McpRequest = z.infer<typeof McpRequestSchema>;

export const BaseResponseSchema = z.object({
  id: z.string(),
  ok: z.boolean(),
});

export const McpResponseSchema = BaseResponseSchema.extend({
  result: z.record(z.string(), z.unknown()).optional(),
  error: z
    .object({
      code: z.string(),
      message: z.string(),
    })
    .optional(),
});

export type McpResponse = z.infer<typeof McpResponseSchema>;