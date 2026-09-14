import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import SignInPage from '../src/app/(auth)/sign-in/page'

describe('SignInPage', () => {
  it('renders sign in form', () => {
    render(<SignInPage />)
    expect(screen.getByText(/welcome back to void/i)).toBeTruthy()
    expect(screen.getByPlaceholderText(/you@example\.com/i)).toBeTruthy()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeTruthy()
  })
})
