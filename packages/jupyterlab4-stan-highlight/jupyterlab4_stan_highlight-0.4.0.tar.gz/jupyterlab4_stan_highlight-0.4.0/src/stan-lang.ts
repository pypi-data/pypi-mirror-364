// @ts-ignore
import { StreamLanguage } from '@codemirror/language';

// Stan language definition for CodeMirror 6
const stan = {
  name: 'stan',

  startState() {
    return {
      tokenize: tokenBase,
      context: null,
      indent: 0,
      startOfLine: true
    };
  },

  token(stream: any, state: any) {
    if (stream.sol()) {
      state.startOfLine = true;
      state.indent = stream.indentation();
    }

    if (stream.eatSpace()) return null;

    state.startOfLine = false;
    return state.tokenize(stream, state);
  },

  indent(state: any, textAfter: string) {
    const { context } = state;
    if (!context) return 0;
    return context.indent + (textAfter.charAt(0) === '}' ? 0 : 2);
  },

  languageData: {
    commentTokens: { line: '//', block: { open: '/*', close: '*/' } },
    closeBrackets: { brackets: ['(', '[', '{', '"'] },
    indentOnInput: /^\s*\}$/
  }
};

// Define tokenize functions outside the object to avoid 'this' issues
function tokenBase(stream: any, state: any): string | null {
  // Comments
  if (stream.match('//')) {
    stream.skipToEnd();
    return 'comment';
  }

  if (stream.match('/*')) {
    state.tokenize = tokenComment;
    return 'comment';
  }

  if (stream.match('#')) {
    // Check for include directive
    if (stream.match(/\s*include\b/)) {
      state.tokenize = tokenInclude;
      return 'meta';
    }
    stream.skipToEnd();
    return 'comment';
  }

  // Numbers
  if (stream.match(/^(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?i?/)) {
    return 'number';
  }

  // Strings
  if (stream.match('"')) {
    state.tokenize = tokenString;
    return 'string';
  }

  // Block keywords
  if (stream.match(/\b(functions|data|transformed\s+data|parameters|transformed\s+parameters|model|generated\s+quantities)\b/)) {
    return 'keyword';
  }

  // Types
  if (stream.match(/\b(int|real|complex|vector|array|simplex|unit_vector|ordered|positive_ordered|row_vector|matrix|corr_matrix|cov_matrix|cholesky_factor_cov|cholesky_factor_corr|void)\b/)) {
    return 'type';
  }

  // Control flow
  if (stream.match(/\b(for|in|while|if|else|return)\b/)) {
    return 'keyword';
  }

  // Distribution sampling
  if (stream.match('~')) {
    return 'operator';
  }

  // Distributions
  if (stream.match(/\b(bernoulli|bernoulli_logit|beta|beta_binomial|binomial|binomial_logit|categorical|categorical_logit|cauchy|chi_square|dirichlet|discrete_range|double_exponential|exp_mod_normal|exponential|frechet|gamma|gaussian_dlm_obs|gumbel|hypergeometric|inv_chi_square|inv_gamma|inv_wishart|lkj_corr|lkj_corr_cholesky|logistic|lognormal|multi_gp|multi_gp_cholesky|multi_normal|multi_normal_cholesky|multi_normal_prec|multi_student_t|multinomial|multinomial_logit|neg_binomial|neg_binomial_2|neg_binomial_2_log|normal|normal_id_glm|ordered_logistic|ordered_probit|pareto|pareto_type_2|poisson|poisson_log|rayleigh|scaled_inv_chi_square|skew_double_exponential|skew_normal|std_normal|student_t|uniform|von_mises|weibull|wiener|wishart)\b/)) {
    return 'builtin';
  }

  // Built-in functions
  if (stream.match(/\b(print|reject|target)\b/)) {
    return 'builtin';
  }

  // Constraints
  if (stream.match(/\b(lower|upper|offset|multiplier)\b/)) {
    return 'keyword';
  }

  // Operators
  if (stream.match(/[+\-*/%^=<>!&|]+|<-/)) {
    return 'operator';
  }

  // Punctuation
  if (stream.match(/[{}()\[\];,]/)) {
    return 'bracket';
  }

  // Identifiers
  if (stream.match(/\b[A-Za-z][0-9A-Za-z_]*\b/)) {
    return 'variable';
  }

  // Illegal identifiers
  if (stream.match(/\b([a-zA-Z0-9_]*__|[0-9_][A-Za-z0-9_]+|_)\b/)) {
    return 'error';
  }

  stream.next();
  return null;
}

function tokenString(stream: any, state: any): string {
  let escaped = false;
  let ch;
  while ((ch = stream.next()) != null) {
    if (ch === '"' && !escaped) {
      state.tokenize = tokenBase;
      break;
    }
    escaped = !escaped && ch === '\\';
  }
  return 'string';
}

function tokenComment(stream: any, state: any): string {
  let maybeEnd = false;
  let ch;
  while ((ch = stream.next()) != null) {
    if (ch === '/' && maybeEnd) {
      state.tokenize = tokenBase;
      break;
    }
    maybeEnd = (ch === '*');
  }
  return 'comment';
}

function tokenInclude(stream: any, state: any): string {
  stream.skipToEnd();
  state.tokenize = tokenBase;
  return 'meta';
}

export const stanLanguage = StreamLanguage.define(stan);

export function stanLang() {
  return stanLanguage;
}
