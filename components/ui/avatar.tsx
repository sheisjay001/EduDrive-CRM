import * as React from "react";
import { cn } from "@/lib/utils";

interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  src?: string;
  alt?: string;
  fallback?: string;
}

const Avatar = React.forwardRef<HTMLDivElement, AvatarProps>(
  ({ className, src, alt, fallback, ...props }, ref) => {
    const [error, setError] = React.useState(false);

    if (src && !error) {
      return (
        <div
          ref={ref}
          className={cn(
            "relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full",
            className
          )}
          {...props}
        >
          <img
            src={src}
            alt={alt}
            className="aspect-square h-full w-full object-cover"
            onError={() => setError(true)}
          />
        </div>
      );
    }

    return (
      <div
        ref={ref}
        className={cn(
          "flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#d9a441]/12 text-[#d9a441] font-medium",
          className
        )}
        {...props}
      >
        {fallback?.charAt(0).toUpperCase()}
      </div>
    );
  }
);
Avatar.displayName = "Avatar";

export { Avatar };
