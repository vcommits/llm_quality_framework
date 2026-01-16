@pytest.mark.drift
def test_drift_with_glider():
    # 1. Subject (Mistral via Together)
    subject = ProviderFactory.get_provider("together", "lite").get_model()

    # 2. Judge (Glider via Hugging Face)
    # We initialize the custom wrapper we made above
    glider = GliderJudge()

    # 3. Metric
    metric = AnswerRelevancyMetric(
        threshold=0.7,
        model=glider,  # <--- Passing Glider here
        include_reason=True  # Glider excels at this
    )

    test_case = LLMTestCase(
        input="What is the capital of France?",
        actual_output=subject.invoke("What is the capital of France?").content
    )

    assert_test(test_case, [metric])