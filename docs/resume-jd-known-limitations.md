# Resume/JD Known Limitations

- Mission and result persistence are in memory and are lost on restart.
- Authentication and project authorization are not implemented.
- PDF extraction requires the `pypdf` dependency and may lose layout information.
- Section-aware extraction for education, experience, projects, and certifications is not complete.
- No external Model Gateway/provider is configured; the local bounded analyzer is used and clearly disclosed.
- Visual formatting, columns, and some ATS behavior cannot be verified from extracted text.
- The recognized skill vocabulary is intentionally small and should be expanded behind a controlled normalization service.
