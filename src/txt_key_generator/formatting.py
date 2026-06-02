from txt_key_generator.schemas import GenerationResult


def format_generation_result(result: GenerationResult) -> str:
    if result.needs_clarification and result.final_text is None:
        questions = result.report.clarifying_questions or [
            "Уточните тему, язык, объем и ключевые слова."
        ]
        joined = "\n".join(f"{index}. {question}" for index, question in enumerate(questions, 1))
        unresolved = ""
        if result.report.violations:
            unresolved = "\n\nНерешенные нарушения:\n" + "\n".join(
                f"- {violation.description}" for violation in result.report.violations
            )
        return f"Нужно уточнение перед финальной выдачей:{unresolved}\n\n{joined}"

    report_lines = [
        "Отчет проверки:",
        f"- Циклов проверки: {result.cycles_used}",
        f"- Score: {result.report.score:.2f}",
        f"- Статус: {'пройдено' if result.report.passed else 'не пройдено'}",
    ]
    if result.report.violations:
        report_lines.append("- Нарушения:")
        report_lines.extend(f"  - {violation.description}" for violation in result.report.violations)

    final_text = result.final_text or ""
    return f"{final_text}\n\n" + "\n".join(report_lines)

