from aiconfig import AIConfigRuntime, InferenceOptions

class RunQuery(object):
    """
    This is a class that runs a query.
    """
    def __init__(self):
        self.config = AIConfigRuntime.load('aiconfig.json')
        self.param = ""

    def get_query(self, input):
        """
        This is a method that runs a query.
        """
        self.param = {"user_input": input}
        
        inference_options = InferenceOptions(stream=True) # Defines a console streaming callback
        result = await self.config.run("cell 4", self.param, options=inference_options)
        return result
        
    def update_url(self, url):
        """
        This is a method that passes in the url
        """
        self.param = {"url": url}
        await self.config.run("cell 3", self.param)
        
        