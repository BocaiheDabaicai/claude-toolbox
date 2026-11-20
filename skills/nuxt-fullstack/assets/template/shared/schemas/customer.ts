import { z } from 'zod'

const optionalText = (max: number) =>
  z
    .string()
    .trim()
    .max(max)
    .optional()
    .nullable()
    .transform((value) => (value ? value : null))

export const customerInputSchema = z.object({
  name: z.string().trim().min(1, '姓名不能为空').max(100, '姓名过长'),
  phone: optionalText(32),
  email: optionalText(255).refine(
    (value) => value === null || /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(value),
    '邮箱格式不正确',
  ),
  company: optionalText(200),
  note: optionalText(2000),
  status: z.enum(['active', 'inactive']).default('active'),
})

export type CustomerInput = z.infer<typeof customerInputSchema>
