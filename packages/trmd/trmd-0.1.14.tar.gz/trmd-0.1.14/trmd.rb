class Trmd < Formula
  include Language::Python::Virtualenv

  desc "Translate Markdown using OpenAI"
  homepage "https://github.com/rioriost/homebrew-trmd/"
  url "https://files.pythonhosted.org/packages/3e/a5/4212a86e4d6e37f73525c4ddf5e775962fd9ed62736e9837be305c7247ee/trmd-0.1.13.tar.gz"
  sha256 "b9f1d7d7e9d2eca1a2f568f0844b61e6a6524d26d0525144857a22749a6b2417"
  license "MIT"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "openai"
  end

  test do
    system "#{bin}/trmd", "--help"
  end
end
