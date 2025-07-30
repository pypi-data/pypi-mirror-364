"""
InfraDSL Serve Command - Start the HTTP/gRPC service
"""

import asyncio
import logging
import signal
import sys
from argparse import ArgumentParser, Namespace
from typing import TYPE_CHECKING

from .base import BaseCommand

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig

logger = logging.getLogger(__name__)


class ServeCommand(BaseCommand):
    """Start the InfraDSL HTTP/gRPC service"""

    @property
    def name(self) -> str:
        return "serve"

    @property
    def description(self) -> str:
        return "Start the HTTP/gRPC service for InfraDSL"

    def register(self, subparsers) -> None:
        """Register command arguments"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Start the InfraDSL HTTP/gRPC service for persistent infrastructure management",
        )

        # Server configuration
        parser.add_argument(
            "--host",
            default="0.0.0.0",
            help="Host to bind the server to (default: 0.0.0.0)"
        )
        parser.add_argument(
            "--port",
            type=int,
            default=8000,
            help="Port to bind the HTTP server to (default: 8000)"
        )
        parser.add_argument(
            "--grpc-port",
            type=int,
            default=8001,
            help="Port to bind the gRPC server to (default: 8001)"
        )

        # Authentication and security
        parser.add_argument(
            "--no-auth",
            action="store_true",
            help="Disable authentication (not recommended for production)"
        )
        parser.add_argument(
            "--disable-rate-limit",
            action="store_true",
            help="Disable rate limiting"
        )
        parser.add_argument(
            "--rate-limit-requests",
            type=int,
            default=100,
            help="Rate limit requests per window (default: 100)"
        )
        parser.add_argument(
            "--rate-limit-window",
            type=int,
            default=60,
            help="Rate limit window in seconds (default: 60)"
        )

        # Service configuration
        parser.add_argument(
            "--http-only",
            action="store_true",
            help="Start only HTTP server (no gRPC)"
        )
        parser.add_argument(
            "--grpc-only",
            action="store_true",
            help="Start only gRPC server (no HTTP)"
        )
        parser.add_argument(
            "--reload",
            action="store_true",
            help="Enable auto-reload for development"
        )
        parser.add_argument(
            "--workers",
            type=int,
            default=1,
            help="Number of worker processes (default: 1)"
        )

        # Development options
        parser.add_argument(
            "--dev",
            action="store_true",
            help="Enable development mode (auto-reload, debug logging)"
        )

        self.add_common_arguments(parser)

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute the serve command"""
        try:
            # Import here to avoid circular imports
            from infradsl.core.service.http_server import NexusAPIServer
            from infradsl.core.service.grpc_server import NexusGRPCService, NexusGRPCServer
            from infradsl.core.nexus import NexusEngine
            
            console.info(f"🚀 Starting InfraDSL Service...")
            
            # Setup development mode
            if args.dev:
                args.reload = True
                logging.basicConfig(level=logging.DEBUG)
                console.info("🔧 Development mode enabled")
            
            # Validate conflicting options
            if args.http_only and args.grpc_only:
                console.error("❌ Cannot use both --http-only and --grpc-only")
                return 1
            
            # Create NexusEngine instance
            nexus_engine = NexusEngine()
            
            # Configure services to start
            start_http = not args.grpc_only
            start_grpc = not args.http_only
            
            # Create servers
            servers = []
            
            if start_http:
                http_server = NexusAPIServer(
                    nexus_engine=nexus_engine,
                    host=args.host,
                    port=args.port,
                    auth_enabled=not args.no_auth,
                    rate_limit_enabled=not args.disable_rate_limit,
                    rate_limit_requests=args.rate_limit_requests,
                    rate_limit_window=args.rate_limit_window,
                )
                servers.append(("HTTP", http_server, args.host, args.port))
                
            if start_grpc:
                grpc_service = NexusGRPCService(nexus_engine=nexus_engine)
                grpc_server = NexusGRPCServer(
                    service=grpc_service,
                    host=args.host,
                    port=args.grpc_port,
                )
                servers.append(("gRPC", grpc_server, args.host, args.grpc_port))
            
            # Start servers
            if args.reload and start_http:
                console.info("🔄 Starting HTTP server with auto-reload...")
                self._start_http_with_reload(args, http_server, console)
            else:
                console.info("🌐 Starting servers...")
                self._start_servers(servers, console)
            
            return 0
            
        except KeyboardInterrupt:
            console.info("\n🛑 Graceful shutdown requested...")
            return 0
        except Exception as e:
            console.error(f"❌ Failed to start service: {e}")
            if console.verbosity >= 2:
                import traceback
                console.error(traceback.format_exc())
            return 1

    def _start_http_with_reload(self, args: Namespace, http_server: "NexusAPIServer", console: "Console") -> None:
        """Start HTTP server with auto-reload using uvicorn"""
        try:
            import uvicorn
            
            console.info(f"🌐 HTTP server starting on http://{args.host}:{args.port}")
            console.info("📡 WebSocket endpoints available at:")
            console.info(f"   • ws://{args.host}:{args.port}/ws/events")
            console.info(f"   • ws://{args.host}:{args.port}/ws/operations/{{id}}")
            console.info(f"   • ws://{args.host}:{args.port}/ws/resources")
            console.info("🔄 Auto-reload enabled - code changes will restart the server")
            console.info("Press Ctrl+C to stop the server")
            
            # Use uvicorn directly with reload
            uvicorn.run(
                http_server.app,
                host=args.host,
                port=args.port,
                reload=True,
                log_level="info" if console.verbosity >= 2 else "warning",
                workers=args.workers if args.workers > 1 else 1,
            )
            
        except ImportError:
            console.error("❌ uvicorn not available. Install with: pip install uvicorn")
            raise
        except Exception as e:
            console.error(f"❌ Failed to start HTTP server: {e}")
            raise

    def _start_servers(self, servers: list, console: "Console") -> None:
        """Start servers without auto-reload"""
        async def run_servers():
            tasks = []
            
            for server_type, server, host, port in servers:
                console.info(f"🌐 {server_type} server starting on {host}:{port}")
                
                if server_type == "HTTP":
                    console.info("📡 WebSocket endpoints available at:")
                    console.info(f"   • ws://{host}:{port}/ws/events")
                    console.info(f"   • ws://{host}:{port}/ws/operations/{{id}}")
                    console.info(f"   • ws://{host}:{port}/ws/resources")
                    
                    # Create HTTP server task
                    task = asyncio.create_task(
                        self._run_http_server(server),
                        name=f"{server_type}-server"
                    )
                    tasks.append(task)
                    
                elif server_type == "gRPC":
                    console.info("🔗 gRPC service endpoints available")
                    
                    # Create gRPC server task
                    task = asyncio.create_task(
                        self._run_grpc_server(server),
                        name=f"{server_type}-server"
                    )
                    tasks.append(task)
            
            console.info("✅ All servers started successfully")
            console.info("Press Ctrl+C to stop the servers")
            
            # Setup signal handlers
            def signal_handler():
                console.info("\n🛑 Graceful shutdown requested...")
                for task in tasks:
                    task.cancel()
            
            # Register signal handlers
            for sig in [signal.SIGTERM, signal.SIGINT]:
                try:
                    loop = asyncio.get_event_loop()
                    loop.add_signal_handler(sig, signal_handler)
                except NotImplementedError:
                    # Windows doesn't support signal handlers in asyncio
                    pass
            
            # Wait for all tasks to complete
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except asyncio.CancelledError:
                console.info("🛑 Servers stopped")
            except Exception as e:
                console.error(f"❌ Server error: {e}")
                raise
        
        # Run the async server setup
        try:
            asyncio.run(run_servers())
        except KeyboardInterrupt:
            console.info("\n🛑 Servers stopped by user")
        except Exception as e:
            console.error(f"❌ Failed to run servers: {e}")
            raise

    async def _run_http_server(self, server: "NexusAPIServer") -> None:
        """Run HTTP server asynchronously"""
        import uvicorn
        
        config = uvicorn.Config(
            app=server.app,
            host=server.host,
            port=server.port,
            log_level="info",
            access_log=True,
        )
        
        server_instance = uvicorn.Server(config)
        await server_instance.serve()

    async def _run_grpc_server(self, server: "NexusGRPCServer") -> None:
        """Run gRPC server asynchronously"""
        await server.start()
        
        # Keep server running
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await server.stop()
            raise