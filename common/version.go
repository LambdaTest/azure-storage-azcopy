package common

// overridden for smooth upgradation experience as this version is tied to the HyperEx CLI
const AzcopyVersion = "10.14.1"

// const AzcopyVersion = "10.30.1"
const UserAgent = "AzCopy/" + AzcopyVersion
const S3ImportUserAgent = "S3Import " + UserAgent
const GCPImportUserAgent = "GCPImport " + UserAgent
const BenchmarkUserAgent = "Benchmark " + UserAgent

// AddUserAgentPrefix appends the global user agent prefix, if applicable
func AddUserAgentPrefix(userAgent string) string {
	prefix := GetEnvironmentVariable(EEnvironmentVariable.UserAgentPrefix())
	if len(prefix) > 0 {
		userAgent = prefix + " " + userAgent
	}

	return userAgent
}
