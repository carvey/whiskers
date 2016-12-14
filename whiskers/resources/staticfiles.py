from twisted.web.resource import Resource

class Static(Resource):

    def getChild(self, path, request):
        static_resource_path = request.postpath