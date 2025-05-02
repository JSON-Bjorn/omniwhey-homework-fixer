# Register all routers here
from app.routes.prds import router as prds_router
from app.routes.collaborations import router as collaborations_router
from app.routes.submissions import router as submissions_router
from app.routes.feedback import router as feedback_router
from app.routes.admin import router as admin_router
from app.routes.docs import router as docs_router
from app.routes.templates import router as templates_router

# Export routers to be included in the main app
routers = [
    prds_router,
    collaborations_router,
    submissions_router,
    feedback_router,
    admin_router,
    docs_router,
    templates_router,
]
