class JobLookupWithConditionError(KeyError):
    """Raised when the job store cannot find a jobs with specific condition."""

    def __init__(self, condition):
        super(JobLookupWithConditionError, self).__init__(u'No jobs with condition: %s was found' % condition)