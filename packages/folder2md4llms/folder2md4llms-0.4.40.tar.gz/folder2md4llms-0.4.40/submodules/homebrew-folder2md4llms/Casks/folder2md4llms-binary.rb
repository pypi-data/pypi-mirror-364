cask "folder2md4llms-binary" do
  version "0.4.37"
  sha256 arm:   "1c4da79e58124eff1ba402fd27cc6166d4070a102b9f0a3c61762faccd4cce70",
         intel: "b3454ad33998689ff93732d80d395d94a7bc022706f2a3e519082bb7c8dfaee9"

  url "https://github.com/HenriquesLab/folder2md4llms/releases/download/v#{version}/folder2md-macos-#{Hardware::CPU.intel? ? "x64" : "arm64"}"
  name "folder2md4llms"
  desc "Enhanced tool to concatenate folder contents into markdown for LLM consumption"
  homepage "https://github.com/henriqueslab/folder2md4llms"

  livecheck do
    url :url
    strategy :github_latest
  end

  binary "folder2md-macos-#{Hardware::CPU.intel? ? "x64" : "arm64"}", target: "folder2md"

  postflight do
    # Ensure the binary is executable
    system_command "/bin/chmod",
                   args: ["+x", "#{staged_path}/folder2md-macos-#{Hardware::CPU.intel? ? "x64" : "arm64"}"]
  end

  test do
    system "#{bin}/folder2md", "--version"
    system "#{bin}/folder2md", "--help"

    # Test basic functionality
    (testpath/"test.py").write("print('hello world')")
    (testpath/"README.md").write("# Test Project")

    # Process the test directory
    system "#{bin}/folder2md", testpath, "--output", "test.md"
    assert_path_exists testpath/"test.md"

    # Check that the output contains expected content
    output_content = File.read(testpath/"test.md")
    assert_match "test.py", output_content
    assert_match "README.md", output_content
    assert_match "Test Project", output_content

    # Test ignore file generation
    system "#{bin}/folder2md", "--init-ignore"
    assert_path_exists testpath/".folder2md_ignore"

    # Verify ignore file has expected content
    ignore_content = File.read(testpath/".folder2md_ignore")
    assert_match "node_modules/", ignore_content
    assert_match "*.pyc", ignore_content
  end

  caveats <<~EOS
    This is the standalone binary version of folder2md4llms.
    
    Advantages:
      ✓ No Python installation required
      ✓ Faster startup time
      ✓ Single executable file
      ✓ No dependency conflicts
    
    For the Python package version (requires Python 3.11+):
      brew install henriqueslab/tap/folder2md4llms
    
    Documentation: https://github.com/henriqueslab/folder2md4llms
  EOS
end