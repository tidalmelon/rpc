package main

import (
    "flag"
    "log"
    "net/http"

    "github.com/grpc-ecosystem/grpc-gateway/runtime"
    "golang.org/x/net/context"
    "google.golang.org/grpc"

    gw "./pb"
)

var (
    loginEndpoint = flag.String("login_endpoint", "localhost:50051", "endpoint of Login Service")
)

func run() error {
    ctx := context.Background()
    ctx, cancel := context.WithCancel(ctx)
    defer cancel()

    mux := runtime.NewServeMux()
    opts := []grpc.DialOption{grpc.WithInsecure()}
    err := gw.RegisterUserLoginHandlerFromEndpoint(ctx, mux, *loginEndpoint, opts)
    if err != nil {
        return err
    }

    log.Print("UserLogin Server start at port 8080...")
    http.ListenAndServe(":8080", mux)
    return nil
}

func main() {
    flag.Parse()

    if err := run(); err != nil {
        log.Fatal(err)
    }
}
