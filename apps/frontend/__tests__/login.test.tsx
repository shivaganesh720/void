import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import LoginPage from '../src/app/login/page'

describe('LoginPage', () => {
  it('renders login form', () => {
    render(<LoginPage />)
    
    expect(screen.getByText(/sign in to your workspace/i)).toBeTruthy()
    expect(screen.getByPlaceholderText(/name@company.com/i)).toBeTruthy()
    expect(screen.getByPlaceholderText(/••••••••/i)).toBeTruthy()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeTruthy()
  })
})
